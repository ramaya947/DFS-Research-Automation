import statsapi, StatWrapper as sw, requests, json
from pybaseball import playerid_reverse_lookup, cache, playerid_lookup

def run():
    cache.enable()
    games = sw.getDaysGames("03/24/2021")
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

    for hitter in hitters:
        print("{} [ {} ]".format(hitter.name, hitter.overall))

    sw.cleanUp()

run()