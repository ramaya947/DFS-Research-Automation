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

def filterStats(entries, filterBy, desiredStats = [], latestYear = None):
    data = {}
    for entry in entries:
        if entry['Season'] == filterBy:
            data = entry

    
        
    response = {}
    for desiredStat in desiredStats:
        if desiredStat in data:
            response[desiredStat] = data[desiredStat]
    
    return response

def getStats(fid, startDate, endDate, groupingType, statType, filters, positionType, desiredStats = []):
    """
   Get Player Stats

   :param str|num fid: The player's fangraphs ID
   :param str startDate: YYYY-MM-DD
   :param str endDate: YYYY-MM-DD
   :param groupingType: Could be season, week, day, month, etc.
   :parm num statType: 1: Standard Stats, 2: Advanced, 3: Batted Balls
   :param array filters: vs L, vs R, etc.
   :param str positionType: P -> Pitcher B -> Batter
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
    body['strPosition'] = positionType
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

PITCHER_STATS_URL = "https://www.fangraphs.com/api/players/splits?playerid={}&position=P&season=0&split=0.{}"

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
                    'handedness': handedness,
                    'vsLocation': 'H'
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
                    'handedness': handedness,
                    'vsLocation': 'A'
                }
            )

        # TODO: Find splits for pitchers
        # Home Pitcher
        if "'" in pitcherHandedness['homeName']:
            pitcherHandedness['homeName'] = pitcherHandedness['homeName'].replace("'", "\\'")
        homePitcherInfo = pocketbase.getPlayer('players', 'name=\'{}\''.format(pitcherHandedness['homeName']), pitcherHandedness['homeName'])
        try:
            pitcherId = homePitcherInfo['pid']
        except:
            print('ERROR: Could not find id for {} in returned Data: {}'.format(pitcherHandedness['homeName'], homePitcherInfo))
            continue
        if homePitcherInfo['fid'] == '':
            data = playerid_reverse_lookup([int(pitcherId)], "mlbam")

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

            homePitcherInfo = pocketbase.updatePlayer('players', homePitcherInfo['id'], { 'fid': '{}'.format(fid) })
            print('Updated entry for {}. FID is now {}'.format(pitcherHandedness['homeName'], homePitcherInfo['fid']))

        # Away Pitcher
        if "'" in pitcherHandedness['awayName']:
            pitcherHandedness['awayName'] = pitcherHandedness['awayName'].replace("'", "\\'")
        awayPitcherInfo = pocketbase.getPlayer('players', 'name=\'{}\''.format(pitcherHandedness['awayName']), pitcherHandedness['awayName'])
        try:
            pitcherId = awayPitcherInfo['pid']
        except:
            print('ERROR: Could not find id for {} in returned Data: {}'.format(pitcherHandedness['awayName'], awayPitcherInfo))
            continue
        if awayPitcherInfo['fid'] == '':
            data = playerid_reverse_lookup([int(pitcherId)], "mlbam")

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

            awayPitcherInfo = pocketbase.updatePlayer('players', awayPitcherInfo['id'], { 'fid': '{}'.format(fid) })
            print('Updated entry for {}. FID is now {}'.format(pitcherHandedness['awayName'], awayPitcherInfo['fid']))

        # Define Stat Types for Pitchers and Batters
        typeStandard = 1
        typeAdvanced = 2
        typeBattedBall = 3

        # Grab Stats for each pitcher
        start = LAST_SEASON_START_DATE
        date = datetime.datetime.strptime(start,"%Y-%m-%d")

        desiredPitcherStats = [
            'IP', 'wOBA', 'BABIP', 'ISO', 'SLG', 'OBP', 'LD%', 'FB%', 'Hard%'
        ]
        #TODO: You are suppose to be getting career stats - minus the current year, and season stats
        # Based on the current date in question.
        homePitcherCareerStatsFiltered = {
            'vsL': {},
            'vsR': {}
        }
        homePitcherCareerStatsFiltered['vsL'].update(getStats(homePitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCareerStatsFiltered['vsL'].update(getStats(homePitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCareerStatsFiltered['vsL'].update(getStats(homePitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCareerStatsFiltered['vsR'].update(getStats(homePitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCareerStatsFiltered['vsR'].update(getStats(homePitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCareerStatsFiltered['vsR'].update(getStats(homePitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pR', 'SP'], "P", desiredPitcherStats)[0])

        homePitcherCurrentStatsFiltered = {
            'vsL': {},
            'vsR': {}
        }
        homePitcherCurrentStatsFiltered['vsL'].update(getStats(homePitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCurrentStatsFiltered['vsL'].update(getStats(homePitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCurrentStatsFiltered['vsL'].update(getStats(homePitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCurrentStatsFiltered['vsR'].update(getStats(homePitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCurrentStatsFiltered['vsR'].update(getStats(homePitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        homePitcherCurrentStatsFiltered['vsR'].update(getStats(homePitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pR', 'SP'], "P", desiredPitcherStats)[0])
    
        awayPitcherCareerStatsFiltered = {
            'vsL': {},
            'vsR': {}
        }
        awayPitcherCareerStatsFiltered['vsL'].update(getStats(awayPitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCareerStatsFiltered['vsL'].update(getStats(awayPitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCareerStatsFiltered['vsL'].update(getStats(awayPitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCareerStatsFiltered['vsR'].update(getStats(awayPitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCareerStatsFiltered['vsR'].update(getStats(awayPitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCareerStatsFiltered['vsR'].update(getStats(awayPitcherInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pR', 'SP'], "P", desiredPitcherStats)[0])

        awayPitcherCurrentStatsFiltered = {
            'vsL': {},
            'vsR': {}
        }
        awayPitcherCurrentStatsFiltered['vsL'].update(getStats(awayPitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCurrentStatsFiltered['vsL'].update(getStats(awayPitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCurrentStatsFiltered['vsL'].update(getStats(awayPitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pL', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCurrentStatsFiltered['vsR'].update(getStats(awayPitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeStandard, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCurrentStatsFiltered['vsR'].update(getStats(awayPitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        awayPitcherCurrentStatsFiltered['vsR'].update(getStats(awayPitcherInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, ['pR', 'SP'], "P", desiredPitcherStats)[0])
        pass

        for player in players:
            playerSoup = soup.find("a", {"title": "{}".format(player['name'])})
            positions = playerSoup.parent.parent.parent.attrs['data-pos']
            battingOrder = playerSoup.parent.parent.parent.find("span", {"class": "order"}).text.strip()
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
                desiredStats = [
                    'PA', 'wOBA', 'BABIP', 'ISO', 'SLG', 'OBP', 'wRC+', 'LD%', 'FB%', 'Hard%'
                ]

                # Set request filters
                requestFilters = []
                requestFilters.append(player['vs'])

                careerStats = {}
                careerStats.update(getStats(playerInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, requestFilters, "B", desiredStats)[0])
                careerStats.update(getStats(playerInfo['fid'], "2002-01-01", (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, requestFilters, "B", desiredStats)[0])

                currentStats = {}
                currentStats.update(getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeAdvanced, requestFilters, "B", desiredStats)[0])
                currentStats.update(getStats(playerInfo['fid'], date.strftime("%Y-%m-%d"), (currDateTime - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "career", typeBattedBall, requestFilters, "B", desiredStats)[0])

                #TODO: Create stats now
                #player['handedness']
                oppPitcherCareer = (homePitcherCareerStatsFiltered if player['vsLocation'] == 'H' else awayPitcherCareerStatsFiltered)['vsL' if player['handedness'] == 'L' else 'vsR']
                if careerStats['PA'] == 0 and oppPitcherCareer['IP'] == 0:
                    continue
                wOBASplitCareer = ((careerStats['wOBA'] if careerStats['PA'] != 0 else oppPitcherCareer['wOBA']) + (oppPitcherCareer['wOBA'] if oppPitcherCareer['IP'] != 0 else careerStats['wOBA'])) / 2
                ISOSplitCareer =  careerStats['ISO']
                SLGSplitCareer = ((careerStats['SLG'] if careerStats['PA'] != 0 else oppPitcherCareer['SLG']) + (oppPitcherCareer['SLG'] if oppPitcherCareer['IP'] != 0 else careerStats['SLG'])) / 2
                OBPSplitCareer = ((careerStats['OBP'] if careerStats['PA'] != 0 else oppPitcherCareer['OBP']) + (oppPitcherCareer['OBP'] if oppPitcherCareer['IP'] != 0 else careerStats['OBP'])) / 2
                LDSplitCareer = ((careerStats['LD%'] if careerStats['PA'] != 0 else oppPitcherCareer['LD%']) + (oppPitcherCareer['LD%'] if oppPitcherCareer['IP'] != 0 else careerStats['LD%'])) / 2
                FBSplitCareer = ((careerStats['FB%'] if careerStats['PA'] != 0 else oppPitcherCareer['FB%']) + (oppPitcherCareer['FB%'] if oppPitcherCareer['IP'] != 0 else careerStats['FB%'])) / 2
                HardFBSplitCareer = ((careerStats['FB%'] * careerStats['Hard%'] if careerStats['PA'] != 0 else oppPitcherCareer['FB%'] * oppPitcherCareer['Hard%']) + (oppPitcherCareer['FB%'] * oppPitcherCareer['Hard%'] if oppPitcherCareer['IP'] != 0 else careerStats['FB%'] * careerStats['Hard%'])) / 2

                orderMultiplier = 1.25 if battingOrder < 6 else 1
                orderedwOBASplitCareer = wOBASplitCareer * orderMultiplier
                orderedISOSplitCareer = ISOSplitCareer * orderMultiplier
                orderedSLGSplitCareer = SLGSplitCareer * orderMultiplier
                orderedOBPSplitCareer = OBPSplitCareer * orderMultiplier
                orderedLDSplitCareer = LDSplitCareer * orderMultiplier
                orderedFBSplitCareer = FBSplitCareer * orderMultiplier
                orderedHardFBSplitCareer = HardFBSplitCareer * orderMultiplier

                # CURRENT STATS
                oppPitcherCurrent = (homePitcherCurrentStatsFiltered if player['vsLocation'] == 'H' else awayPitcherCurrentStatsFiltered)['vsL' if player['handedness'] == 'L' else 'vsR']
                if currentStats['PA'] == 0 and oppPitcherCurrent['IP'] == 0:
                    continue
                wOBASplitCurrent = ((currentStats['wOBA'] if currentStats['PA'] != 0 else oppPitcherCurrent['wOBA']) + (oppPitcherCurrent['wOBA'] if oppPitcherCurrent['IP'] != 0 else currentStats['wOBA'])) / 2
                ISOSplitCurrent =  currentStats['ISO']
                SLGSplitCurrent = ((currentStats['SLG'] if currentStats['PA'] != 0 else oppPitcherCurrent['SLG']) + (oppPitcherCurrent['SLG'] if oppPitcherCurrent['IP'] != 0 else currentStats['SLG'])) / 2
                OBPSplitCurrent = ((currentStats['OBP'] if currentStats['PA'] != 0 else oppPitcherCurrent['OBP']) + (oppPitcherCurrent['OBP'] if oppPitcherCurrent['IP'] != 0 else currentStats['OBP'])) / 2
                LDSplitCurrent = ((currentStats['LD%'] if currentStats['PA'] != 0 else oppPitcherCurrent['LD%']) + (oppPitcherCurrent['LD%'] if oppPitcherCurrent['IP'] != 0 else currentStats['LD%'])) / 2
                FBSplitCurrent = ((currentStats['FB%'] if currentStats['PA'] != 0 else oppPitcherCurrent['FB%']) + (oppPitcherCurrent['FB%'] if oppPitcherCurrent['IP'] != 0 else currentStats['FB%'])) / 2
                HardFBSplitCurrent = ((currentStats['FB%'] * currentStats['Hard%'] if currentStats['PA'] != 0 else oppPitcherCurrent['FB%'] * oppPitcherCurrent['Hard%']) + (oppPitcherCurrent['FB%'] * oppPitcherCurrent['Hard%'] if oppPitcherCurrent['IP'] != 0 else currentStats['FB%'] * currentStats['Hard%'])) / 2

                orderMultiplier = 1.25 if battingOrder < 6 else 1
                orderedwOBASplitCurrent = wOBASplitCurrent * orderMultiplier
                orderedISOSplitCurrent = ISOSplitCurrent * orderMultiplier
                orderedSLGSplitCurrent = SLGSplitCurrent * orderMultiplier
                orderedOBPSplitCurrent = OBPSplitCurrent * orderMultiplier
                orderedLDSplitCurrent = LDSplitCurrent * orderMultiplier
                orderedFBSplitCurrent = FBSplitCurrent * orderMultiplier
                orderedHardFBSplitCurrent = HardFBSplitCurrent * orderMultiplier

                bReality = (currentStats['BABIP'] if currentStats['PA'] != 0 else 1) / (careerStats['BABIP'] if careerStats['PA'] != 0 else 1)
                pReality = (oppPitcherCurrent['BABIP'] if oppPitcherCurrent['IP'] != 0 else 1) / (oppPitcherCareer['BABIP'] if oppPitcherCareer['IP'] != 0 else 1)

                wOBASplitReal = ((currentStats['wOBA'] if currentStats['PA'] != 0 else oppPitcherCurrent['wOBA']) * (1 / bReality) + (oppPitcherCurrent['wOBA'] if oppPitcherCurrent['IP'] != 0 else currentStats['wOBA']) * (1 / pReality)) / 2

                #TODO: It seems to be pairing the incorrect pitchjer and batter

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

                #stats = getStats(playerInfo['fid'], "2022-04-05", "2022-04-25", "season", 2)
                #print(stats)
            #break
        #break


# TODO: I just realized that I don't think these stats are filtered by handedness...