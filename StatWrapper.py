import csv, statsapi, datetime, PitcherClass, HitterClass, requests, json, TeamAverages, LeagueAverages
from pybaseball import playerid_reverse_lookup

PLAYER_STATS_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position={}&season={}&split=&z=1614959387TEAM_CHANGE"
teamAvg = TeamAverages.TeamAverages()
leagueAvg = LeagueAverages.LeagueAverages()
file = open("MissingPlayerIds.csv", "a+")
manualFill = True
parkFactors = json.loads(open("ParkFactors.json", "r").read())

def cleanUp():
    file.close()

#Get games for either today or a specified day
def getDaysGames(mf, date = None):
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
    return games

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
        url = PLAYER_STATS_URL.format(pid, pos, adjustedYear)
        data = requests.get(url)
        data = json.loads(data.text)
        #print("Data from {}".format(url))
        #print(data)

        if (len(data) == 0):
            offset += 1
            continue

        for obj in data:
            if obj['Split'] == "vs L":
                statsL = obj
                statsL['season'] = obj['Season']
            elif obj['Split'] == "vs R":
                statsR = obj
                statsR['season'] = obj['Season']

    stats = { 'vsL': statsL, 'vsR': statsR }
    return stats

def sortPitchers(pitchers):
    pitchers.sort(key=lambda x: x.overall, reverse=True)
    pSize = len(pitchers)
    pitcherSet = {"use": [], "target": []}
    if pSize == 0:
        print("No probable pitchers")
    elif pSize == 1:
        print("Only 1 available pitcher")
        pitcherSet = { "use": [pitchers[0]], "target": [pitchers[0]]}
    
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
        teamKey = teamAvg.getTeamKey(player.teamName)

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
                    pass
            lineCount += 1
        
        FDFile.seek(0)
    
    FDFile.close()
    return result

def writeSummary(players, pitchers, hrList):
    summaryFile = open("Summary.txt", "w")

    pSet = sortPitchers(pitchers)

    output = "Pitchers to use:\n"
    for pitcher in pSet["use"]:
        output += "\t{} ${} [{}] vs {} - Overall: {} K% Average: {} K% vs L: {} K% vs R: {}\n".format(pitcher.name, pitcher.salary, pitcher.teamName, pitcher.oppTeamName, round(pitcher.overall, 2), pitcher.kRate['avg'], pitcher.kRate['vsL'], pitcher.kRate['vsR'])
    output += "Catchers to use:\n"
    for p in players['C']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / p.salary), 2))
    output += "First Basemen to use:\n"
    for p in players['1B']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / p.salary), 2))
    output += "Second Basemen to use:\n"
    for p in players['2B']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / p.salary), 2))
    output += "Third Basemen to use:\n"
    for p in players['3B']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / p.salary), 2))
    output += "Shortstops to use:\n"
    for p in players['SS']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / p.salary), 2))
    output += "OutFielders to use:\n"
    for p in players['OF']: 
        output += "\t{} ${} [{}] vs {} - Overall: {} HR Rating: {} Value Rating: {}\n".format(p.name, p.salary, p.teamName, p.oppPitcher.name, round(p.overall, 2), round(p.hrRating, 2), round((p.overall / p.salary), 2))

    output += "HR Ratings, Ranked\n"
    for h in hrList:
        output += "\t{} - HR Rating: {}\n".format(h.name, h.hrRating)

    summaryFile.write(output)
    summaryFile.close()