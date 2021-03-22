import mlbgame
import AnalyzePitchers, AnalyzeHitters
from pybaseball import cache
import Pitcher
import TeamAverages

games = mlbgame.day(2021, 3, 17)

cache.enable()

pitchers = AnalyzePitchers.AnalyzePitchers(games)

for p in pitchers.pitcherSet["use"]:
            print("Use {} vs {} with Rating: {}".format(p.fullName, p.oppTeam, round(p.avgRating, 2)))

for p in pitchers.pitcherSet["target"]:
            print("Target {} vs {} with Rating: {}".format(p.fullName, p.oppTeam, round(p.avgRating, 2)))

hitters = AnalyzeHitters.AnalyzeHitters(pitchers.pitcherSet["target"])

output = ""
for h in hitters.hitters:
    output += "Hitter {} vs {}\n".format(h.fullName, h.oppPitcher.fullName)

file = open("Hitters.txt", "w")
file.write(output)
file.close()