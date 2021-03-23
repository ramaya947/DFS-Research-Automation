import statsapi, datetime, PitcherClass, requests, json, TeamAverages, LeagueAverages
from pybaseball import playerid_reverse_lookup

PITCHER_STATS_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position=P&season={}&split=&z=1614959387TEAM_CHANGE"
teamAvg = TeamAverages.TeamAverages()
leagueAvg = LeagueAverages.LeagueAverages()

#Get games for either today or a specified day
def getDaysGames(date = None):
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

def getGamesProbablePitchers(game, pitchers):
    homeRoster = getTeamRoster(game["home_id"])["roster"]
    awayRoster = getTeamRoster(game["away_id"])["roster"]
    pitcherHome = game["home_probable_pitcher"]
    pitcherAway = game["away_probable_pitcher"]

    pitcher = None
    for p in homeRoster:
        if pitcherHome in p["person"]["fullName"]:
            print("Found {} with pid: {}".format(pitcherHome, p["person"]["id"]))
            pitcher = PitcherClass.PitcherClass(p, teamAvg, leagueAvg)
            pitcher.fid = getFangraphsId(pitcher)
            pitcher.stats = getMostRecentStats(pitcher.fid)
            pitcher.setOtherInformation(setOtherInfo(game, "home"))
            pitcher.handedness = getPitcherHandedness(statsapi.get('person', {'personId': str(pitcher.pid)}))
            if pitcher.stats['vsL'] != None and pitcher.stats['vsR'] != None:
                pitcher.assessSelf()
                pitchers.append(pitcher)
    for p in awayRoster:
        if pitcherHome in p["person"]["fullName"]:
            print("Found {} with pid: {}".format(pitcherAway, p["person"]["id"]))
            pitcher = PitcherClass.PitcherClass(p, teamAvg, leagueAvg)
            pitcher.fid = getFangraphsId(pitcher)
            pitcher.stats = getMostRecentStats(pitcher.fid)
            pitcher.setOtherInformation(setOtherInfo(game, "away"))
            pitcher.handedness = getPitcherHandedness(statsapi.get('person', {'personId': str(pitcher.pid)}))
            if pitcher.stats != None:
                pitcher.assessSelf()
                pitchers.append(pitcher)

def setOtherInfo(data, location):
    info = {
        'oppTeamId': data['away_id'] if location == "home" else data['home_id'],
        'oppTeamName': data['away_name'] if location == "home" else data['home_name'],
        'teamId': data['home_id'] if location == "home" else data['away_id'],
        'teamName': data['home_name'] if location == "home" else data['away_name'],
        'stadiumId': data['venue_id'],
        'stadiumName': data['venue_name']
    }

    return info

def getPitcherHandedness(data):
    player = data['people'][0]
    handedness = player['pitchHand']['code']
    
    return handedness

def getFangraphsId(pitcher):
    data = playerid_reverse_lookup([pitcher.pid], "mlbam")
    
    fid = None
    try:
        fid = data.at[0, "key_fangraphs"]
    except:
        print("Couldn't get fangraphs ID for {}".format(pitcher.name))

    return fid

def getMostRecentStats(pid):
    d = datetime.datetime.now()
    year = d.year
    statsL = None
    statsR = None
    offset = 0
    while (offset <= 2 and statsL == None and statsR == None):
        adjustedYear = year - offset
        url = PITCHER_STATS_URL.format(pid, adjustedYear)
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