import statsapi, StatWrapper as sw, requests, json, datetime
from pybaseball import playerid_reverse_lookup, cache, playerid_lookup
from dateutil import tz
import LeagueAverages

def run(manualFill, slateStart, date, compare):
    print("\n\n\nYou are still defaulting to year 2020 for stats due to limited sample size, adjust when ready\n\n\n")
    cache.enable()
    games = sw.getDaysGames(manualFill, slateStart, compare, False, date)
    pitchers = []
    hitters = []
    for game in games:
        sw.getGamesProbablePitchers(game, pitchers)

    sw.assessPitchers(pitchers)
    pitchers.sort(key=lambda x: x.overall, reverse=True)

    for pitcher in pitchers:
        sw.createHitters(pitcher, hitters)
        print("{} is facing off against the {} [ {} ]".format(pitcher.name, pitcher.oppTeamName, round(pitcher.overall, 2)))
        print("Total Innings Pitched: {}".format(pitcher.stats['vsL']['IP'] + pitcher.stats['vsR']['IP']))

    sw.assessHitters(hitters)

    hitters.sort(key=lambda x: x.overall, reverse=True)

    hitters = sw.getPlayerSalaries(hitters)

    players = {"C": [], "1B": [], "2B": [], "3B": [], "SS": [], "OF": []}
    for hitter in hitters:
        #print("({}) {} [ {} ]".format(hitter.position, hitter.name, hitter.overall))
        try:
            players[hitter.position].append(hitter)
        except Exception as e:
            print(e)
    
    sw.getPlayerSalaries(pitchers)

    hitters.sort(key=lambda x: x.hrRating, reverse=True)
    sw.writeSummary(players, pitchers, hitters)
    sw.writeSummaryToCSV(hitters, pitchers)
    sw.cleanUp()

manualFill = False
ss = datetime.datetime(2021, 4, 7, 13, 10, 0)
date = "04/07/2021"
run(manualFill, ss, date, "after")