import datetime, statsapi
from dateutil import tz

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

def getDaysGames(mf, slateStart, compare, getImpliedTotals, date = None):
    if date == None:
        dt = datetime.datetime.now()
        date = datetime.datetime.strftime(dt, "%m/%d/%Y")
        
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
    
for game in getDaysGames(1,1,1,1,None):
    print(game)