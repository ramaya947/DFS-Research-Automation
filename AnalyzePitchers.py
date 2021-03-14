##This will analyze probable pitchers and return an object with arrays of pitchers to use
##And pitchers to target
import mlbgame
import LeagueAverages
import Pitcher
import TeamAverages

class AnalyzePitchers:
    leagueAverages = None
    probablePitchers = []
    pitcherSet = {
        "use": [],
        "target": []
    }
    errorLog = None

    def __init__(self, games):
        self.errorLog = open("ErrorLog.txt", "a")
        self.leagueAverages = LeagueAverages.LeagueAverages().averages
        self.analyzeGames(games)
        self.analyzePitcherSplits()
        self.sortPitchers()
        self.errorLog.close()

    def sortPitchers(self):
        self.probablePitchers.sort(key=lambda x: x.avgRating, reverse=True)
        pSize = len(self.probablePitchers)
        if pSize == 0:
            print("No probable pitchers")
        elif pSize == 1:
            print("Only 1 available pitcher")
            self.pitcherSet = { "use": [self.probablePitchers[0]], "target": [self.probablePitchers[0]]}
        
        for x in range(0, pSize):
            pitcher = self.probablePitchers[x]
            if (x / (pSize - 1)) >= .75:
                self.pitcherSet["use"].append(pitcher)
            else:
                self.pitcherSet["target"].append(pitcher)


    def analyzeGames(self, games):
        homePitcher = ""
        awayPitcher = ""
        for game in games:
            pitchers = []

            if not(hasattr(game, "p_pitcher_home")) or not(hasattr(game, "p_pitcher_away")):
                continue

            homePitcher = game.p_pitcher_home
            awayPitcher = game.p_pitcher_away

            pitchers.append({ "name": homePitcher, "oppTeam": game.home_team, "team": game.away_team})  #This shouldn't be this way, may change after Spring Training
            pitchers.append({ "name": awayPitcher, "oppTeam": game.away_team, "team": game.home_team})  #This shouldn't be this way, may change after Spring Training
            self.getPitcherData(pitchers)
            #break #REMOVE - TESTING
    
    def getPitcherData(self, pitchers):
        for pitcher in pitchers:
            name = pitcher["name"]
            oppTeam = pitcher["oppTeam"]
            team = pitcher["team"]
            p = Pitcher.Pitcher(name, oppTeam, team)
            if p.playerId is not None and p.rawStatData != None:
                self.probablePitchers.append(p)
            #break #REMOVE - TESTING

    def analyzePitcherSplits(self):
        vsL = {}
        vsR = {}
        pitchingStatsToUse = ["BB%", "K%", "BABIP", "AVG", "wOBA"]
        hittingStatsToUse = ["BB%", "K%", "ISO", "BABIP", "wOBA"]
        t = TeamAverages.TeamAverages()
        for pitcher in self.probablePitchers:
            try:
                vsL = pitcher.rawStatData[0]
                vsR = pitcher.rawStatData[1]
                debugKey = ""

                for key in pitchingStatsToUse:
                    lgAvg = self.leagueAverages[key]
                    debugKey = key
                    if key == "BB%":
                        if vsL[key] >= lgAvg:
                            pitcher.ratingL += (vsL[key] / lgAvg) * 1
                            #Pitcher allows worse than league average base on balls rate vs L
                        if vsR[key] >= lgAvg:
                            pitcher.ratingR += (vsR[key] / lgAvg) * 1
                            #Pitcher allows worse than league average base on balls rate vs R
                    elif key == "K%":
                        if vsL[key] <= lgAvg:
                            pitcher.ratingL += (lgAvg / vsL[key]) * 1
                            #Pitchers strikes out less than lg avg vs L
                        else:
                            pitcher.ratingL -= (vsL[key] / lgAvg) * 1
                        if vsR[key] <= lgAvg:
                            pitcher.ratingR += (lgAvg / vsR[key]) * 1
                            #Pitchers strikes out less than lg avg vs R
                        else:
                            pitcher.ratingR -= (vsR[key] / lgAvg) * 1
                    elif key == "BABIP":
                        if vsL[key] >= lgAvg:
                            pitcher.ratingL += (vsL[key] / lgAvg) * 1.5
                            #Pitcher is unlucky vs L
                        else:
                            pitcher.ratingL -= (lgAvg / vsL[key]) * 1.5
                        if vsR[key] >= lgAvg:
                            pitcher.ratingR += (vsR[key] / lgAvg) * 1.5
                            #Pitcher is unlucky vs R
                        else:
                            pitcher.ratingR -= (lgAvg / vsR[key]) * 1.5
                    elif key == "AVG":
                        if vsL[key] >= lgAvg:
                            pitcher.ratingL += (vsL[key] / lgAvg) * 1
                            #Pitcher gives up a lot of hits vs L
                        if vsR[key] >= lgAvg:
                            pitcher.ratingR += (vsR[key] / lgAvg) * 1
                            #Pitcher gives up a lot of hits vs R
                    elif key == "wOBA":
                        if vsL[key] >= lgAvg:
                            pitcher.ratingL += (vsL[key] / lgAvg) * 2
                            #Pitcher gives up big hits against L
                        else:
                            pitcher.ratingL -= (lgAvg / vsL[key]) * 2
                        if vsR[key] >= lgAvg:
                            pitcher.ratingR += (vsR[key] / lgAvg) * 2
                            #Pitcher gives up big hits against R
                        else:
                            pitcher.ratingR -= (lgAvg / vsR[key]) * 2
                pitcher.calcAvgRating()

            except Exception as e:
                errorString = "Error getting stats for {}. key = {}\n".format(pitcher.fullName, debugKey)
                self.errorLog.write(repr(e) + '\n' + errorString)
                continue
            
            try:
                oppTeamKey = t.getTeamKey(pitcher.oppTeam)
                teamStats = t.averages[oppTeamKey]

                #["BB%", "K%", "ISO", "BABIP", "OPS", "wOBA"]
                for key in hittingStatsToUse:
                    lgAvg = self.leagueAverages[key]
                    teamStat = teamStats[key]
                    debugKey = key
                    
                    if key == "BB%":
                        if teamStat >= lgAvg:
                            pitcher.avgRating += (teamStat / lgAvg) * 1
                    elif key == "K%":
                        if teamStat <= lgAvg:
                            pitcher.avgRating += (lgAvg / teamStat) * 1
                        else:
                            pitcher.avgRating -= (teamStat / lgAvg) * 1
                    elif key == "ISO":
                        if teamStat >= lgAvg:
                            pitcher.avgRating += (teamStat / lgAvg) * 1.5
                        else:
                            pitcher.avgRating -= (lgAvg / teamStat) * 1.5
                    elif key == "BABIP":
                        if teamStat >= lgAvg:
                            pitcher.avgRating += (teamStat / lgAvg) * 1.5
                        else:
                            pitcher.avgRating -= (lgAvg / teamStat) * 1.5
                    elif key == "wOBA":
                        if teamStat >= lgAvg:
                            pitcher.avgRating += (teamStat / lgAvg) * 2
                        else:
                            pitcher.avgRating -= (lgAvg / teamStat) * 2

            except Exception as e:
                errorString = "Error with team: {}. key = {}, val = {}\n".format(pitcher.oppTeam, debugKey, lgAvg)
                self.errorLog.write(rep(e) + '\n' + errorString)
                continue
        #Now compare to stats of opposing teams
            