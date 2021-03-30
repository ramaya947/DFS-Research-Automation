import statsapi, StatWrapper as sw, requests, json
from pybaseball import playerid_reverse_lookup, cache, playerid_lookup

def run(manualFill):
    cache.enable()
    games = sw.getDaysGames(manualFill, "03/29/2021")
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

    sw.writeSummary(players, pitchers)
    sw.cleanUp()

manualFill = False
run(manualFill)