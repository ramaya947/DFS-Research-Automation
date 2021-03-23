import statsapi, StatWrapper as sw, requests, json
from pybaseball import playerid_reverse_lookup, cache

def run():
    games = sw.getDaysGames("03/22/2021")
    pitchers = []
    for game in games:
        sw.getGamesProbablePitchers(game, pitchers)

    for pitcher in pitchers:
        print("{} is facing off against the {} [ {} ]".format(pitcher.name, pitcher.oppTeamName, pitcher.overall))

cache.enable()
run()