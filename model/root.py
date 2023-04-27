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

LAST_SEASON_START_DATE = "2022-04-01"
LAST_SEASON_END_DATE = "2022-10-28"

file = open("MissingPlayerIds.csv", "a+")

# First: Grab his total points for that day
url = "https://rotogrinders.com/lineups/mlb?date={}&site=fanduel"
date = "2022-04-08"
formattedUrl = url.format(date)

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
            type = 2

            date = datetime.datetime.strptime(start,"%Y-%m-%d")
            endDate = datetime.datetime.strptime(end,"%Y-%m-%d")
            dateDelta = datetime.timedelta(days = 1)

            prevYearDelta = datetime.timedelta(days = 365)
            prevYearDate = (date - prevYearDelta).strftime("%Y-%m-%d")
            prevYearEndDate = (endDate - prevYearDelta).strftime("%Y-%m-%d")
            
            lastYearCareerStats = getStats(playerInfo['fid'], prevYearDate, prevYearEndDate, "season", type)
            
            # Add stats to PB DB
            response = pocketbase.addEntireSeasonsStats("seasonStats", {
                "pid": playerId,
                "stats": lastYearCareerStats,
                "season": (date - prevYearDelta).year,
                "type": type
            })

            print(response)
            #while(date <= endDate):
                # "{}-{}-{}".format(date.year, date.month, date.day)


            #    date += dateDelta
            

            #stats = getStats(playerInfo['fid'], "2022-04-05", "2022-04-25", "season", 2)
            #print(stats)
        break
    break

