from bs4 import BeautifulSoup
import requests, statsapi, csv, json, datetime
import pocketbase.PocketbaseProxy as pocketbase
from pybaseball import playerid_reverse_lookup

# POC
# Grab the stats for Mike Trout for the second game of last season
#   This means:
#       - Career stats for time period prior to that game
#       - Season stats up to that date
# The date was 2022-04-08

def getStats(fid, startDate, endDate, groupingType, statType):
    """
   Get Player Stats

   :param str|num fid: The player's fangraphs ID
   :param str startDate: YYYY-MM-DD
   :param str endDate: YYYY-MM-DD
   :param groupingType: Could be season, week, day, month, etc.
   :parm num statType: 1: Standard Stats, 2: Advanced, 3: Batted Balls
   :return: Player stats
   :rtype: Object
   """
    
    body = json.load(open('./model/constants/RequestBodys.JSON', 'r'))['datedPlayerSplitsStats']
    
    body['strPlayerId'] = fid
    body['strStartDate'] = startDate
    body['strEndDate'] = endDate
    body['strGroup'] = groupingType
    body['strType'] = statType

    response = requests.post(DATED_PLAYER_SPLITS_STATS_URL, json = body)

    return json.loads(response.text)['data']

PLAYER_STATS_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position={}&season={}&split=&z=1614959387TEAM_CHANGE"
DATED_PLAYER_SPLITS_STATS_URL = "https://www.fangraphs.com/api/leaders/splits/splits-leaders"

LAST_SEASON_START_DATE = "2022-04-07"
LAST_SEASON_END_DATE = "2022-10-28"

file = open("MissingPlayerIds.csv", "a+")

# Setup datetime objects for loop
currDate = "2022-04-23"
currDateTime = datetime.datetime.strptime(currDate, "%Y-%m-%d")

while currDateTime <= (datetime.datetime.strptime(currDate, "%Y-%m-%d") + datetime.timedelta(days = 20)):
    currDateTime += datetime.timedelta(days = 1)
    
    # First: Grab his total points for that day
    url = "https://rotogrinders.com/lineups/mlb?date={}&site=fanduel"
    formattedUrl = url.format(currDateTime.strftime("%Y-%m-%d"))

    # Make request
    data = requests.get(formattedUrl)
    soup = BeautifulSoup(data.text)
    cards = soup.find_all("div", {"class": "blk crd lineup"})

    #Find all the players for that day
    for card in cards:
        teamsSoup = card.find("div", {"class": "teams"}).find_all("span", {"class": "shrt"})
        awayTeam = teamsSoup[0].text
        homeTeam = teamsSoup[1].text

        players = []
        battingOrderSoup = card.find("div", {"class": "blk away-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
        for player in battingOrderSoup:
            name = player.find("a", {"class": "player-popup"}).text
            players.append(name)
        
        battingOrderSoup = card.find("div", {"class": "blk home-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
        for player in battingOrderSoup:
            name = player.find("a", {"class": "player-popup"}).text
            players.append(name)

        for player in players:
            playerSoup = soup.find("a", {"title": "{}".format(player)})
            positions = playerSoup.parent.parent.parent.attrs['data-pos']
            fpts = playerSoup.parent.parent.find("span", {"title": "Fantasy Points"}).text
            if fpts and fpts != None and fpts != "" and fpts != "" and fpts != '':
                if "'" in player:
                    player = player.replace("'", "\\'")
                print("{}: {}".format(player, fpts))
                playerInfo = pocketbase.getPlayer('players', 'name=\'{}\''.format(player), player)
                try:
                    playerId = playerInfo['pid']
                except:
                    print('ERROR: Could not find id for {} in returned Data: {}'.format(player, playerInfo))
                    continue

                if playerInfo['fid'] == '':
                    data = playerid_reverse_lookup([int(playerId)], "mlbam")

                    fid = None
                    try:
                        fid = data.at[0, "key_fangraphs"]
                    except Exception as e: print(e)

                    if fid == None:
                        file.seek(0)
                        csv_reader = csv.reader(file, delimiter=',')
                        line_count = 0
                        for row in csv_reader:
                            if line_count > 0:
                                try:
                                    if row[0] == playerId:
                                        fid = row[1]
                                        break
                                except:
                                    pass
                            line_count += 1
                        if fid == None:
                            print("Failed final attempt to get player fangraphsId for {}".format(player))
                            continue

                    playerInfo = pocketbase.updatePlayer('players', playerInfo['id'], { 'fid': '{}'.format(fid) })
                    print('Updated entry for {}. FID is now {}'.format(player, playerInfo['fid']))
                


                # Now that we have both pid and fid, start grabbing stats for the player

                start = LAST_SEASON_START_DATE
                end = LAST_SEASON_END_DATE
                typeStandard = 1
                typeAdvanced = 2
                typeBattedBall = 3

                date = datetime.datetime.strptime(start,"%Y-%m-%d")
                endDate = datetime.datetime.strptime(end,"%Y-%m-%d")
                dateDelta = datetime.timedelta(days = 1)

                prevYearDelta = datetime.timedelta(days = 365)
                prevYearDate = (date - prevYearDelta).strftime("%Y-%m-%d")
                prevYearEndDate = (endDate - prevYearDelta).strftime("%Y-%m-%d")
                
                lastYearStandardStats = getStats(playerInfo['fid'], prevYearDate, prevYearEndDate, "season", typeStandard)
                
                # Add stats to PB DB
                lastYearStandardStats = pocketbase.addEntireSeasonsStats("seasonStats", {
                    "pid": playerId,
                    "stats": lastYearStandardStats,
                    "season": (date - prevYearDelta).year,
                    "type": typeStandard
                })

                lastYearAvancedStats = getStats(playerInfo['fid'], prevYearDate, prevYearEndDate, "season", typeAdvanced)
                
                # Add stats to PB DB
                lastYearAvancedStats = pocketbase.addEntireSeasonsStats("seasonStats", {
                    "pid": playerId,
                    "stats": lastYearAvancedStats,
                    "season": (date - prevYearDelta).year,
                    "type": typeAdvanced
                })

                lastYearBattedBallStats = getStats(playerInfo['fid'], prevYearDate, prevYearEndDate, "season", typeBattedBall)
                
                # Add stats to PB DB
                lastYearBattedBallStats = pocketbase.addEntireSeasonsStats("seasonStats", {
                    "pid": playerId,
                    "stats": lastYearBattedBallStats,
                    "season": (date - prevYearDelta).year,
                    "type": typeBattedBall
                })

                d = datetime.datetime.strptime(currDate, "%Y-%m-%d")
                ########################################################################
                # Get stats for current season up to this date
                standardCurrSeasonStats = getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeStandard)
                # If standardCurrSeasonStats is empty, then skip this player. They didn't have any prev performance data to go off of for this season, yet.
                if len(standardCurrSeasonStats) == 0:
                    continue

                # If not, continue on
                advancedCurrSeasonStats = getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeAdvanced)
                battedBallCurrSeasonStats = getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeBattedBall)
                ########################################################################

                ########################################################################
                # Get stats for last week of current season
                standardLastWeekStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 1, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeStandard)
                advancedLastWeekStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 1, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeAdvanced)
                battedBallLastWeekStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 1, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeBattedBall)
                ########################################################################

                ########################################################################
                # Get stats for last 2 weeks of current season
                standardLastTwoWeeksStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 2, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeStandard)
                advancedLastTwoWeeksStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 2, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeAdvanced)
                battedBallLastTwoWeeksStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 2, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeBattedBall)
                ########################################################################

                # TODO: Add to performance table
                performanceRecord = pocketbase.addPerformanceRecord('performances', {
                    "pid": playerId,
                    "positions": positions,
                    "date": currDateTime.strftime("%Y-%m-%d"),
                    "fpts": float(fpts),
                    "standardCurrSeasonStats": standardCurrSeasonStats,
                    "advancedCurrSeasonStats": advancedCurrSeasonStats,
                    "battedBallCurrSeasonStats": battedBallCurrSeasonStats,
                    "standardLastWeekStats": standardLastWeekStats,
                    "advancedLastWeekStats": advancedLastWeekStats,
                    "battedBallLastWeekStats": battedBallLastWeekStats,
                    "standardTwoWeekStats": standardLastTwoWeeksStats,
                    "advancedTwoWeekStats": advancedLastTwoWeeksStats,
                    "battedBallTwoWeekStats": battedBallLastTwoWeeksStats
                })
                #while(date <= endDate):
                    # "{}-{}-{}".format(date.year, date.month, date.day)


                #    date += dateDelta
                

                #stats = getStats(playerInfo['fid'], "2022-04-05", "2022-04-25", "season", 2)
                #print(stats)
            #break
        #break

