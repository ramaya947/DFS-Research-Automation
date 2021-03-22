import statsapi, StatWrapper as sw, requests, json

def run():
    games = sw.getDaysGames("03/21/2021")
    pitchers = []
    for game in games:
        sw.getGamesProbablePitchers(game, pitchers)

    for pitcher in pitchers:
        print("{} is facing off against the {}\nHere are their stats".format(pitcher.name, pitcher.oppTeamName))
        print(pitcher.stats)

run()