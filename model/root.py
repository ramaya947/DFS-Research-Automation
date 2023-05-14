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

def getStats(fid, startDate, endDate, groupingType, statType, filters, desiredStats = []):
    """
   Get Player Stats

   :param str|num fid: The player's fangraphs ID
   :param str startDate: YYYY-MM-DD
   :param str endDate: YYYY-MM-DD
   :param groupingType: Could be season, week, day, month, etc.
   :parm num statType: 1: Standard Stats, 2: Advanced, 3: Batted Balls
   :param array filters: vs L, vs R, etc.
   :param array desiredStats: The stats that you want to be returned
   :return: Player stats
   :rtype: Object
   """
    
    RequestBodyJSON = json.load(open('./model/constants/RequestBodys.JSON', 'r'))

    requestFilters = []
    for filter in filters:
        requestFilters.append(RequestBodyJSON['vs'][filter])

    body = RequestBodyJSON['datedPlayerSplitsStats']
    
    body['strPlayerId'] = fid
    body['strStartDate'] = startDate
    body['strEndDate'] = endDate
    body['strGroup'] = groupingType
    body['strType'] = statType
    body['strSplitArr'] = requestFilters

    response = requests.post(DATED_PLAYER_SPLITS_STATS_URL, json = body)
    data = json.loads(response.text)['data']
    if len(desiredStats) == 0:
        return data

    data = data[0]
    response = {}
    for desiredStat in desiredStats:
        if desiredStat in data:
            response[desiredStat] = data[desiredStat]

    return [response]

PLAYER_STATS_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position={}&season={}&split=&z=1614959387TEAM_CHANGE"
DATED_PLAYER_SPLITS_STATS_URL = "https://www.fangraphs.com/api/leaders/splits/splits-leaders"

LAST_SEASON_START_DATE = "2022-04-07"
LAST_SEASON_END_DATE = "2022-10-28"

file = open("MissingPlayerIds.csv", "a+")

# Setup datetime objects for loop
currDate = "2022-04-23"
currDateTime = datetime.datetime.strptime(currDate, "%Y-%m-%d")

while currDateTime <= (datetime.datetime.strptime(currDate, "%Y-%m-%d") + datetime.timedelta(days = 90)):
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

        # Find pitcher and get handedness
        pitcherHandedness = { 'away': None, 'home': None, 'awayName': None, 'homeName': None }
        # Find Away Pitcher first
        awaySoup = card.find("div", {"class": "blk away-team"})
        awayPitcherSoup = awaySoup.find("div", {"class": "pitcher players"}).find("span", {"class": "meta stats"})
        pitcherHandedness['awayName'] = awaySoup.find("div", {"class": "pitcher players"}).find("a", {"class": "player-popup"}).text
        pitcherHandedness['away'] = awayPitcherSoup.find("span", { "class": "stats"}).text.strip()

        # Now find Home Pitcher
        homeSoup = card.find("div", {"class": "blk home-team"})
        homePitcherSoup = homeSoup.find("div", {"class": "pitcher players"}).find("span", {"class": "meta stats"})
        pitcherHandedness['homeName'] = homeSoup.find("div", {"class": "pitcher players"}).find("a", {"class": "player-popup"}).text
        pitcherHandedness['home'] = homePitcherSoup.find("span", { "class": "stats"}).text.strip()

        players = []
        battingOrderSoup = card.find("div", {"class": "blk away-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
        for player in battingOrderSoup:
            name = player.find("a", {"class": "player-popup"}).text
            handedness = player.find("span", {"class": "stats"}).find("span", {"class": "stats"}).text.strip()
            players.append(
                {
                    'name': name,
                    'vs': pitcherHandedness['home'],
                    'handedness': handedness
                }
            )
        
        battingOrderSoup = card.find("div", {"class": "blk home-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
        for player in battingOrderSoup:
            name = player.find("a", {"class": "player-popup"}).text
            handedness = player.find("span", {"class": "stats"}).find("span", {"class": "stats"}).text.strip()
            players.append(
                {
                    'name': name,
                    'vs': pitcherHandedness['home'],
                    'handedness': handedness
                }
            )

        # TODO: Find splits for pitchers

        for player in players:
            playerSoup = soup.find("a", {"title": "{}".format(player['name'])})
            positions = playerSoup.parent.parent.parent.attrs['data-pos']
            battingOrder = positions = playerSoup.parent.parent.parent.find("span", {"class": "order"}).text.strip()
            if battingOrder.isdigit():
                battingOrder = int(battingOrder)
            fpts = playerSoup.parent.parent.find("span", {"title": "Fantasy Points"}).text
            if fpts and fpts != None and fpts != "" and fpts != "" and fpts != '':
                if "'" in player['name']:
                    player['name'] = player['name'].replace("'", "\\'")
                playerInfo = pocketbase.getPlayer('players', 'name=\'{}\''.format(player['name']), player['name'])
                try:
                    playerId = playerInfo['pid']
                except:
                    print('ERROR: Could not find id for {} in returned Data: {}'.format(player['name'], playerInfo))
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
                            print("Failed final attempt to get player fangraphsId for {}".format(player['name']))
                            continue

                    playerInfo = pocketbase.updatePlayer('players', playerInfo['id'], { 'fid': '{}'.format(fid) })
                    print('Updated entry for {}. FID is now {}'.format(player['name'], playerInfo['fid']))
                


                # Now that we have both pid and fid, start grabbing stats for the player

                start = LAST_SEASON_START_DATE
                end = LAST_SEASON_END_DATE
                typeStandard = 1
                typeAdvanced = 2
                typeBattedBall = 3

                desiredAdvancedStats = [
                    'wOBA', 'BABIP', 'ISO', 'SLG', 'OBP', 'wRC+'
                ]
                desiredBattedBallStats = [
                    'LD%', 'FB%', 'Hard%'
                ]

                date = datetime.datetime.strptime(start,"%Y-%m-%d")
                endDate = datetime.datetime.strptime(end,"%Y-%m-%d")
                dateDelta = datetime.timedelta(days = 1)

                prevYearDelta = datetime.timedelta(days = 365)
                prevYearDate = (date - prevYearDelta).strftime("%Y-%m-%d")
                prevYearEndDate = (endDate - prevYearDelta).strftime("%Y-%m-%d")

                # Set request filters
                requestFilters = []
                requestFilters.append(player['vs'])

                lastYearAvancedStats = getStats(playerInfo['fid'], prevYearDate, prevYearEndDate, "season", typeAdvanced, requestFilters, desiredAdvancedStats)
                
                # Add stats to PB DB
                lastYearAvancedStats = pocketbase.addEntireSeasonsStats("seasonStats", {
                    "pid": playerId,
                    "stats": lastYearAvancedStats,
                    "season": (date - prevYearDelta).year,
                    "type": typeAdvanced
                })

                lastYearBattedBallStats = getStats(playerInfo['fid'], prevYearDate, prevYearEndDate, "season", typeBattedBall, requestFilters, desiredBattedBallStats)
                
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
                advancedCurrSeasonStats = getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeAdvanced, requestFilters, desiredAdvancedStats)
                # If standardCurrSeasonStats is empty, then skip this player. They didn't have any prev performance data to go off of for this season, yet.
                # If not, continue on
                if len(advancedCurrSeasonStats) == 0:
                    continue
                battedBallCurrSeasonStats = getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeBattedBall, requestFilters, desiredBattedBallStats)
                ########################################################################

                ########################################################################
                # Get stats for last week of current season
                advancedLastWeekStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 1, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeAdvanced, requestFilters, desiredAdvancedStats)
                battedBallLastWeekStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 1, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeBattedBall, requestFilters, desiredBattedBallStats)
                ########################################################################

                ########################################################################
                # Get stats for last 2 weeks of current season
                advancedLastTwoWeeksStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 2, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeAdvanced, requestFilters, desiredAdvancedStats)
                battedBallLastTwoWeeksStats = getStats(playerInfo['fid'], (d - datetime.timedelta(weeks = 2, days = 1)).strftime("%Y-%m-%d"), (d - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "season", typeBattedBall, requestFilters, desiredBattedBallStats)
                ########################################################################

                # TODO: Add to performance table
                performanceRecord = pocketbase.addPerformanceRecord('performances', {
                    "pid": playerId,
                    "positions": positions,
                    "date": currDateTime.strftime("%Y-%m-%d"),
                    "fpts": float(fpts),
                    "advancedCurrSeasonStats": advancedCurrSeasonStats,
                    "battedBallCurrSeasonStats": battedBallCurrSeasonStats,
                    "advancedLastWeekStats": advancedLastWeekStats,
                    "battedBallLastWeekStats": battedBallLastWeekStats,
                    "advancedTwoWeekStats": advancedLastTwoWeeksStats,
                    "battedBallTwoWeekStats": battedBallLastTwoWeeksStats
                })
                pass
                #while(date <= endDate):
                    # "{}-{}-{}".format(date.year, date.month, date.day)


                #    date += dateDelta
                

                #stats = getStats(playerInfo['fid'], "2022-04-05", "2022-04-25", "season", 2)
                #print(stats)
            #break
        #break


# TODO: I just realized that I don't think these stats are filtered by handedness...