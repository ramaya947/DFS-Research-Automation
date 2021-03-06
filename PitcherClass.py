class PitcherClass:
    pid = None
    fid = None
    fanduelID = None
    name = None
    position = None
    salary = None
    FDPos = None
    handedness = None
    oppTeamId = None
    oppTeamName = None
    oppTeamRoster = None
    teamId = None
    teamName = None
    stadiumId = None
    stadiumName = None
    stats = None
    oppMatchupStats = None
    parkFactors = None
    overall = None
    kRate = None
    ratingL = None
    ratingR = None
    teamAvgs = None
    leagueAvgs = None
    pitchers = None
    gameInfo = None
    homeOrAway = None
    gameCard = None

    def __init__(self, data, teamAvgs, leagueAvgs, oppRoster, gameInfo, parkFactors):
        self.pid = data['person']['id']
        self.name = data['person']['fullName']
        self.position = data['position']['abbreviation']
        self.teamAvgs = teamAvgs
        self.leagueAvgs = leagueAvgs
        self.ratingL = 0.0
        self.ratingR = 0.0
        self.overall = 0.0
        self.kRate = {
            "avg": 0.0,
            "vsL": 0.0,
            "vsR": 0.0,
            "opp": 0.0
        }
        self.stats = {}
        self.oppTeamRoster = oppRoster
        self.gameInfo = gameInfo
        self.parkFactors = parkFactors

    def setOtherInformation(self, data, rgl):
        self.oppTeamId = data['oppTeamId']
        self.oppTeamName = data['oppTeamName']
        self.teamId = data['teamId']
        self.teamName = data['teamName']
        self.stadiumId = data['stadiumId']
        self.stadiumName = data['stadiumName']
        self.home = data['homeOrAway']
        self.gameCard = rgl.getGameCard(self.teamName)

    def assessSelf(self, avgIP):
        pitcherStats = {}
        vsL = {}
        vsR = {}
        pitchingStatsToUse = ["BB%", "K%", "BABIP", "AVG", "wOBA"]
        hittingStatsToUse = ["BB%", "K%", "ISO", "BABIP", "wOBA"]

        vsL = self.stats['vsL']
        vsR = self.stats['vsR']

        for key in pitchingStatsToUse:
            try:
                lgAvg = self.leagueAvgs.averages[key]
                debugKey = key
                if key == "BB%":
                    if vsL[key] >= lgAvg:
                        self.ratingL += (vsL[key] / lgAvg) * 1
                        #Pitcher allows worse than league average base on balls rate vs L
                    if vsR[key] >= lgAvg:
                        self.ratingR += (vsR[key] / lgAvg) * 1
                        #Pitcher allows worse than league average base on balls rate vs R
                elif key == "K%":
                    if vsL[key] <= lgAvg:
                        self.ratingL += (lgAvg / vsL[key]) * 1
                        #Pitchers strikes out less than lg avg vs L
                    else:
                        self.ratingL -= (vsL[key] / lgAvg) * 1.5
                    if vsR[key] <= lgAvg:
                        self.ratingR += (lgAvg / vsR[key]) * 1
                        #Pitchers strikes out less than lg avg vs R
                    else:
                        self.ratingR -= (vsR[key] / lgAvg) * 1.5
                    self.kRate["avg"] = (vsR[key] + vsL[key]) / 2
                    self.kRate["vsL"] = vsL[key]
                    self.kRate["vsR"] = vsR[key]
                elif key == "BABIP":
                    if vsL[key] >= lgAvg:
                        self.ratingL += (vsL[key] / lgAvg) * 1.5
                        #Pitcher is unlucky vs L
                    else:
                        self.ratingL -= (lgAvg / vsL[key]) * 1.5
                    if vsR[key] >= lgAvg:
                        self.ratingR += (vsR[key] / lgAvg) * 1.5
                        #Pitcher is unlucky vs R
                    else:
                        self.ratingR -= (lgAvg / vsR[key]) * 1.5
                elif key == "AVG":
                    if vsL[key] >= lgAvg:
                        self.ratingL += (vsL[key] / lgAvg) * 1
                        #Pitcher gives up a lot of hits vs L
                    if vsR[key] >= lgAvg:
                        self.ratingR += (vsR[key] / lgAvg) * 1
                        #Pitcher gives up a lot of hits vs R
                elif key == "wOBA":
                    if vsL[key] >= lgAvg:
                        self.ratingL += (vsL[key] / lgAvg) * 2
                        #Pitcher gives up big hits against L
                    else:
                        self.ratingL -= (lgAvg / vsL[key]) * 2
                    if vsR[key] >= lgAvg:
                        self.ratingR += (vsR[key] / lgAvg) * 2
                        #Pitcher gives up big hits against R
                    else:
                        self.ratingR -= (lgAvg / vsR[key]) * 2

            except ZeroDivisionError as e:
                #errorString = "Error getting stats for {}. key = {}\n".format(self.name, debugKey)
                #print(e)
                pass

        self.calcAvgRating()

        oppTeamKey = self.teamAvgs.getTeamKey(self.oppTeamName)
        teamStats = self.teamAvgs.averages['vsL'][oppTeamKey] if self.handedness == "L" else self.teamAvgs.averages['vsR'][oppTeamKey]
        self.oppMatchupStats = teamStats

        #["BB%", "K%", "ISO", "BABIP", "OPS", "wOBA"]
        for key in hittingStatsToUse:
            try:
                lgAvg = self.leagueAvgs.averages[key]
                teamStat = teamStats[key]
                debugKey = key
                
                if key == "BB%":
                    if teamStat >= lgAvg:
                        self.overall += (teamStat / lgAvg) * 1
                elif key == "K%":
                    if teamStat <= lgAvg:
                        self.overall += (lgAvg / teamStat) * 1
                    else:
                        self.overall -= (teamStat / lgAvg) * 1
                    self.kRate["opp"] = teamStat
                elif key == "ISO":
                    if teamStat >= lgAvg:
                        self.overall += (teamStat / lgAvg) * 1.5
                    else:
                        self.overall -= (lgAvg / teamStat) * 1.5
                elif key == "BABIP":
                    if teamStat >= lgAvg:
                        self.overall += (teamStat / lgAvg) * 1.5
                    else:
                        self.overall -= (lgAvg / teamStat) * 1.5
                elif key == "wOBA":
                    if teamStat >= lgAvg:
                        self.overall += (teamStat / lgAvg) * 2
                    else:
                        self.overall -= (lgAvg / teamStat) * 2
            except ZeroDivisionError as e:
                pass
                #print(e)
        
        self.applyInningWeight(avgIP)

    def calcAvgRating(self):
        self.overall = (self.ratingL + self.ratingR) / 2

    def applyInningWeight(self, avgIP):
        innings = self.stats['vsL']['IP'] + self.stats['vsR']['IP']
        factor = (innings /avgIP)
        self.overall = self.overall * factor