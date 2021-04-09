import csv, statsapi, datetime, PitcherClass, HitterClass, requests, json, TeamAverages, LeagueAverages
from pybaseball import playerid_reverse_lookup
from dateutil import tz
from openpyxl import Workbook

PLAYER_STATS_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position={}&season={}&split=&z=1614959387TEAM_CHANGE"
teamAvg = TeamAverages.TeamAverages()
leagueAvg = LeagueAverages.LeagueAverages()
file = open("MissingPlayerIds.csv", "a+")
manualFill = True
parkFactors = json.loads(open("ParkFactors.json", "r").read())

def cleanUp():
    file.close()

def filterTime(game, slateStart, compare):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    dt = datetime.datetime.strptime(game['game_datetime'], "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=from_zone)
    local = dt.astimezone(to_zone)
    
    if compare == "before":
        if local.time() <= slateStart.time():
            return True
        else:
            return False
    elif compare == "after":
        if local.time() >= slateStart.time():
            return True
        else:
            return False

#Get games for either today or a specified day
def getDaysGames(mf, slateStart, compare, getImpliedTotals, date = None):
    global manualFill
    manualFill = mf

    if date == None:
        dt = datetime.datetime.now()
        
        day = ""
        if dt.day < 10:
            day = "0{}".format(dt.day)
        else:
            day = dt.day

        month = ""
        if dt.month < 10:
            month = "0{}".format(dt.month)
        else:
            month = dt.month
        
        year = dt.year
        
        date = "{}/{}/{}".format(month, day, year)
    
    games = statsapi.schedule(date)
    filteredGames = []
    for game in games:
        if filterTime(game, slateStart, compare):
            filteredGames.append(game)

    for game in filteredGames:
        if getImpliedTotals:
            game['impliedTotals'] = getTeamsImpliedTotals(game)

    return filteredGames

def getTeamsImpliedTotals(game):
    set = {}
    homeTotal = input("Please provide the implied total for {}:\n ".format(game['home_name']))
    awayTotal = input("Please provide the implied total for {}:\n ".format(game['away_name']))
    set['homeTotal'] = homeTotal
    set['awayTotal'] = awayTotal
    set['combinedTotal'] = homeTotal + awayTotal

    return set

def getGamebyID(gid):
    game = statsapi.schedule(game_id=gid)
    return game

def getTeamRoster(teamId):
    data = statsapi.get("team_roster", {"teamId": teamId})
    return data

def getPlayerInfo(name):
    data = statsapi.lookup_player(name)
    return data

def createHitters(pitcher, hitters):
    roster = pitcher.oppTeamRoster

    for player in roster:
        #Create hitter
        hitter = HitterClass.HitterClass(player, leagueAvg, pitcher)
        if hitter.position == "P":
            continue
        hitter.fid = getFangraphsId(hitter)
        if hitter.fid == None:
            continue
        hitter.stats = getMostRecentStats(hitter.fid, hitter.position)
        hitter.setOtherInformation(setHitterOtherInfo(pitcher.gameInfo, pitcher.home))
        hitter.handedness = getPitcherHandedness(statsapi.get('person', {'personId': str(hitter.pid)}))

        hitters.append(hitter)

def getGamesProbablePitchers(game, pitchers):
    homeRoster = getTeamRoster(game["home_id"])["roster"]
    awayRoster = getTeamRoster(game["away_id"])["roster"]
    pitcherHome = game["home_probable_pitcher"]
    pitcherAway = game["away_probable_pitcher"]
    try:
        parkFactorsForVenue = parkFactors[game['venue_name']]
    except Exception as e:
        print("\n\n\nError in getting Park Factors: {}\nCould not get Park Factors for {}\n\n\n".format(str(e), game['venue_name']))
        parkFactorsForVenue = {"runs": 0, "hr": 0}

    print("{} vs {}".format(pitcherHome, pitcherAway))

    pitcher = None
    if pitcherHome != '':
        for p in homeRoster:
            if pitcherHome in p["person"]["fullName"]:
                print("Found {} with pid: {}".format(pitcherHome, p["person"]["id"]))
                pitcher = PitcherClass.PitcherClass(p, teamAvg, leagueAvg, awayRoster, game, parkFactorsForVenue)
                pitcher.fid = getFangraphsId(pitcher, manualFill)
                if pitcher.fid == None:
                    continue
                pitcher.stats = getMostRecentStats(pitcher.fid, 'P')
                pitcher.setOtherInformation(setOtherInfo(game, "home"))
                pitcher.handedness = getPitcherHandedness(statsapi.get('person', {'personId': str(pitcher.pid)}))
                if pitcher.stats['vsL'] != None and pitcher.stats['vsR'] != None:
                    #pitcher.assessSelf()
                    pitchers.append(pitcher)
                else:
                    pitcher.fid = askUserForFID(pitcher.name)
                    if pitcher.fid == None:
                        continue
                    pitcher.stats = getMostRecentStats(pitcher.fid, 'P')
                    if pitcher.stats['vsL'] != None and pitcher.stats['vsR'] != None:
                        #pitcher.assessSelf()
                        pitchers.append(pitcher)
    if pitcherAway != '':
        for p in awayRoster:
            if pitcherAway in p["person"]["fullName"]:
                print("Found {} with pid: {}".format(pitcherAway, p["person"]["id"]))
                pitcher = PitcherClass.PitcherClass(p, teamAvg, leagueAvg, homeRoster, game, parkFactorsForVenue)
                pitcher.fid = getFangraphsId(pitcher)
                if pitcher.fid == None:
                    continue
                pitcher.stats = getMostRecentStats(pitcher.fid, 'P')
                pitcher.setOtherInformation(setOtherInfo(game, "away"))
                pitcher.handedness = getPitcherHandedness(statsapi.get('person', {'personId': str(pitcher.pid)}))
                if pitcher.stats['vsL'] != None and pitcher.stats['vsR'] != None:
                    #pitcher.assessSelf()
                    pitchers.append(pitcher)
                else:
                    pitcher.fid = askUserForFID(pitcher.name)
                    if pitcher.fid == None:
                        continue
                    pitcher.stats = getMostRecentStats(pitcher.fid, 'P')
                    if pitcher.stats['vsL'] != None and pitcher.stats['vsR'] != None:
                        #pitcher.assessSelf()
                        pitchers.append(pitcher)

def assessPitchers(pitchers):
    totalInnings = 0
    for pitcher in pitchers:
        totalInnings += pitcher.stats['vsL']['IP'] + pitcher.stats['vsR']['IP']
    
    avgIP = totalInnings / len(pitchers)

    for pitcher in pitchers:
        pitcher.assessSelf(avgIP)

def assessHitters(hitters):
    avgPA = 0
    count = 0
    for hitter in hitters:
        if hitter.position != 'P':
            vsLPA = 0
            try:
                vsLPA = hitter.stats['vsL']['PA']
            except:
                vsLPA = 0
            vsRPA = 0
            try:
                vsLPA = hitter.stats['vsR']['PA']
            except:
                vsLPA = 0
            avgPA +=  vsLPA + vsRPA
            count += 1
    avgPA = avgPA / count

    for hitter in hitters:
        if hitter.position != "P":
            hitter.assessSelf(avgPA)

def setHitterOtherInfo(data, location):
    info = {
        'oppTeamId': data['away_id'] if location == "away" else data['home_id'],
        'oppTeamName': data['away_name'] if location == "away" else data['home_name'],
        'teamId': data['home_id'] if location == "away" else data['away_id'],
        'teamName': data['home_name'] if location == "away" else data['away_name'],
        'stadiumId': data['venue_id'],
        'stadiumName': data['venue_name'],
    }

    return info

def setOtherInfo(data, location):
    info = {
        'oppTeamId': data['away_id'] if location == "home" else data['home_id'],
        'oppTeamName': data['away_name'] if location == "home" else data['home_name'],
        'teamId': data['home_id'] if location == "home" else data['away_id'],
        'teamName': data['home_name'] if location == "home" else data['away_name'],
        'stadiumId': data['venue_id'],
        'stadiumName': data['venue_name'],
        'homeOrAway': location
    }

    return info

def getPitcherHandedness(data):
    player = data['people'][0]
    handedness = player['pitchHand']['code']
    
    return handedness

def getFangraphsId(player, retrying = None):
    data = playerid_reverse_lookup([player.pid], "mlbam")
    
    fid = None
    try:
        fid = data.at[0, "key_fangraphs"]
    except:
        print("Couldn't get fangraphs ID for {}".format(player.name))
        if retrying == None:
            return checkInCsvRecords(player.pid, player.name)

    if fid == -1 and retrying == None:
        return checkInCsvRecords(player.pid, player.name)

    return fid

def checkInCsvRecords(pid, name):
    file.seek(0)
    csv_reader = csv.reader(file, delimiter=',')
    line_count = 0
    fid = None
    for row in csv_reader:
        if line_count > 0:
            try:
                if row[0] == str(pid):
                    fid = row[1]
                    return fid
            except:
                pass
        line_count += 1
    
    #Player Not Found
    fid = askUserForFID(name)
    if fid == None or fid == "":
        return None

    file.write("{},{},\n".format(pid, fid))
    return fid

def askUserForFID(name):
    if not manualFill:
        return None

    fid = input("Please provide {}'s confirmed Fangraphs ID:\n".format(name))

    if fid == None or fid == "":
        print("Returning None")
        return None
    else:
        return fid

def getMostRecentStats(pid, pos):
    d = datetime.datetime.now()
    year = d.year
    statsL = None
    statsR = None
    offset = 0
    while (offset <= 2 and statsL == None and statsR == None):
        adjustedYear = year - offset

        if adjustedYear == 2021:
            offset += 1
            continue
        #TODO: REMOVE WHEN 2021 SAMPLE SIZE IS LARGE ENOUGH

        url = PLAYER_STATS_URL.format(pid, pos, adjustedYear)
        data = requests.get(url)
        data = json.loads(data.text)
        #print("Data from {}".format(url))
        #print(data)

        if (len(data) == 0):
            offset += 1
            continue

        for obj in data:
            try:
                if obj['Split'] == "vs L":
                    statsL = obj
                    statsL['season'] = obj['Season']
                elif obj['Split'] == "vs R":
                    statsR = obj
                    statsR['season'] = obj['Season']
            except:
                pass

    stats = { 'vsL': statsL, 'vsR': statsR }
    return stats

def sortPitchers(pitchers):
    pitchers.sort(key=lambda x: x.overall, reverse=True)
    pSize = len(pitchers)
    pitcherSet = {"use": [], "target": []}
    if pSize == 0:
        print("No probable pitchers")
        return pitcherSet
    elif pSize == 1:
        print("Only 1 available pitcher")
        pitcherSet = { "use": [pitchers[0]], "target": [pitchers[0]]}
        return pitcherSet
    
    for x in range(0, pSize):
        pitcher = pitchers[x]
        if (x / (pSize - 1)) >= .75:
            pitcherSet["use"].append(pitcher)
        else:
            pitcherSet["target"].append(pitcher)
    
    return pitcherSet

def getPlayerSalaries(players):
    FDFile = open("FDPlayerList.csv", "r")
    FDFile.seek(0)
    result = []

    for player in players:
        name = player.name
        teamKey = teamAvg.getFanduelTeamKey(player.teamName)

        lineCount = 0
        csv_reader = csv.reader(FDFile, delimiter=',')
        for row in csv_reader:
            if lineCount > 0:
                try:
                    csvName = "{} {}".format(row[2], row[4])
                    if name == csvName and teamKey == row[9]:
                        player.salary = row[7]
                        result.append(player)
                except:
                    player.salary = -1000
            lineCount += 1
        
        FDFile.seek(0)
    
    FDFile.close()
    return result

def getStacks(players):
    stacks = {}
    addedTeams = []

    for player in players:
        if player.overall <= 0.0:
            continue

        team = player.teamName
        if team not in addedTeams:
            addedTeams.append(team)
            stacks[team] = {}
            stacks[team]['totalOverall'] = 0.0
            stacks[team]['playerList'] = []

        stacks[team]['totalOverall'] += player.overall
        stacks[team]['playerList'].append(player)

    result = []
    for team in addedTeams:
        var = {
            "team": team,
            "averageOverall": stacks[team]['totalOverall'] / len(stacks[team]['playerList']),
            "players": stacks[team]['playerList']
        }
        result.append(var)
    result.sort(key=lambda x: x['averageOverall'], reverse=True)
    return result

def writeSummary(players, pitchers, hrList):
    summaryFile = open("Summary.txt", "w")

    pSet = sortPitchers(pitchers)

    output = "Pitchers to use:\n"
    for pitcher in pSet["use"]:
        output += "\t{} ${} [{}] vs {} - Overall: {} K% Average: {} K% vs L: {} K% vs R: {}\n".format(pitcher.name, pitcher.salary, pitcher.teamName, pitcher.oppTeamName, round(pitcher.overall, 2), round(pitcher.kRate['avg'], 2), round(pitcher.kRate['vsL'], 2), round(pitcher.kRate['vsR'], 2))
    output += "\nPitchers to target:\n"
    for pitcher in pSet["target"]:
        output += "\t{} ${} [{}] vs {} - Overall: {} K% Average: {} K% vs L: {} K% vs R: {}\n".format(pitcher.name, pitcher.salary, pitcher.teamName, pitcher.oppTeamName, round(pitcher.overall, 2), round(pitcher.kRate['avg'], 2), round(pitcher.kRate['vsL'], 2), round(pitcher.kRate['vsR'], 2))
    output += "\nCatchers to use:\n"
    for p in players['C']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / (float(p.salary) / 1000)), 2))
    output += "\nFirst Basemen to use:\n"
    for p in players['1B']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / (float(p.salary) / 1000)), 2))
    output += "\nSecond Basemen to use:\n"
    for p in players['2B']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / (float(p.salary) / 1000)), 2))
    output += "\nThird Basemen to use:\n"
    for p in players['3B']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / (float(p.salary) / 1000)), 2))
    output += "\nShortstops to use:\n"
    for p in players['SS']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / (float(p.salary) / 1000)), 2))
    output += "\nOutFielders to use:\n"
    for p in players['OF']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / (float(p.salary) / 1000)), 2))

    output += "\nHR Ratings, Ranked\n"
    for h in hrList:
        output += "\t{} - HR Rating: {} Overall: {}\n".format(h.name, h.hrRating, h.overall)
    output += "\nStacks to Consider:\n"
    for team in getStacks(hrList):
        output += "{} - Avg Overall: {}\n".format(team['team'], team['averageOverall'])
        for p in team['players']:
            output += "\t[{}] {} ${} - Overall: {} Value Rating: {}\n".format(p.position, p.name, p.salary, round(p.overall, 2), round((p.overall / (float(p.salary) / 1000)), 2))

    summaryFile.write(output)
    summaryFile.close()

def writeSummaryToCSV(hitters, pitchers):
    wb = Workbook()
    #Create Hitters Sheet
    #hitterSheet = wb.create_sheet("Hitters")
    #Create Pitchers Sheet
    pitcherSheet = wb.create_sheet("Pitchers")

    #Append Hitters
    positions = ["C", "1B", "2B", "3B", "SS", "OF"]
    for pos in positions:
        sheet = wb.create_sheet(pos)
        appendRow = ["Pos", "Name", "Team", "Salary", "Hand", "Opp Pitcher", "Overall", "Value", "wOBA", "Opp wOBA", "ISO", "Opp ISO", "BABIP", "Opp BABIP", "HR Rating", "Park HR Factor"]
        sheet.append(appendRow)
        for hitter in hitters[pos]:
            appendRow = []
            appendRow.append(hitter.position)
            appendRow.append(hitter.name)
            appendRow.append(hitter.teamName)
            appendRow.append(hitter.salary)
            appendRow.append(hitter.handedness)
            appendRow.append(hitter.oppPitcher.name)
            appendRow.append(round(hitter.overall, 2))
            appendRow.append(round((hitter.overall / (float(hitter.salary) / 1000)), 2))

            if hitter.matchupStats == None:
                appendRow.append(0)
                appendRow.append(0)
                appendRow.append(0)
                appendRow.append(0)
                appendRow.append(0)
                appendRow.append(0)
            else:
                appendRow.append(hitter.matchupStats['wOBA'])
                appendRow.append(hitter.oppMatchupStats['wOBA'])
                appendRow.append(hitter.matchupStats['ISO'])
                appendRow.append(hitter.oppMatchupStats['ISO'])
                appendRow.append(hitter.matchupStats['BABIP'])
                appendRow.append(hitter.oppMatchupStats['BABIP'])
            appendRow.append(hitter.hrRating)
            appendRow.append(hitter.parkFactors['hr'])

            sheet.append(appendRow)

    appendRow = ["Name", "Team", "Salary", "Hand", "Opp Team", "Overall", "Value", "K% vs L", "K% vs R", "Opp K%", "wOBA", "Opp wOBA", "ISO", "Opp ISO", "BABIP", "Opp BABIP", "Park HR Factor"]
    pitcherSheet.append(appendRow)
    for pitcher in pitchers:
        appendRow = []
        appendRow.append(pitcher.name)
        appendRow.append(pitcher.teamName)
        appendRow.append(pitcher.salary)
        appendRow.append(pitcher.handedness)
        appendRow.append(pitcher.oppTeamName)
        appendRow.append(round(pitcher.overall, 2))
        appendRow.append(round((hitter.overall / (float(pitcher.salary) / 1000)), 2))
        appendRow.append(pitcher.kRate['vsL'])
        appendRow.append(pitcher.kRate['vsR'])
        appendRow.append(pitcher.kRate['opp'])
        appendRow.append(round((pitcher.stats['vsL']['wOBA'] + pitcher.stats['vsR']['wOBA']) / 2, 2))
        appendRow.append(pitcher.oppMatchupStats['wOBA'])
        appendRow.append(round((pitcher.stats['vsL']['ISO'] + pitcher.stats['vsR']['ISO']) / 2, 2))
        appendRow.append(pitcher.oppMatchupStats['ISO'])
        appendRow.append(round((pitcher.stats['vsL']['BABIP'] + pitcher.stats['vsR']['BABIP']) / 2, 2))
        appendRow.append(pitcher.oppMatchupStats['BABIP'])
        appendRow.append(pitcher.parkFactors['hr'])
        
        pitcherSheet.append(appendRow)

    wb.save("Summary.xlsx")