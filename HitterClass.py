class HitterClass:
    pid = None
    fid = None
    name = None
    position = None
    salary = None
    handedness = None
    oppPitcher = None
    teamId = None
    teamName = None
    stadiumId = None
    stadiumName = None
    stats = None
    hrRating = None
    parkFactors = None
    overall = None
    leagueAvgs = None
    matchupStats = None
    oppMatchupStats = None

    def __init__(self, data, leagueAvgs, pitcher):
        self.pid = data['person']['id']
        self.name = data['person']['fullName']
        self.position = self.getPositionForOutfielder(data['position']['abbreviation'])
        self.leagueAvgs = leagueAvgs
        self.overall = 0.0
        self.stats = {}
        self.oppPitcher = pitcher
        self.hrRating = 0.0
        self.parkFactors = pitcher.parkFactors

    def getPositionForOutfielder(self, pos):
        if pos in ["OF", "LF", "CF", "RF"]:
            return "OF"
        else:
            return pos

    def setOtherInformation(self, data):
        self.teamId = data['teamId']
        self.teamName = data['teamName']
        self.stadiumId = data['stadiumId']
        self.stadiumName = data['stadiumName']

    def assessSelf(self, avgPA):
        ps = self.oppPitcher.stats['vsL'] if self.handedness == "L" else self.oppPitcher.stats['vsR']
        ps['ISO'] = ps['SLG'] - ps['AVG']
        hs = self.stats['vsL'] if self.oppPitcher.handedness == "L" else self.stats['vsR']

        if hs == None:
            return

        self.matchupStats = hs
        self.oppMatchupStats = ps

        #First compare to league Average
        hittingStatsToUse = ["BB%", "K%", "ISO", "BABIP", "wOBA"]
        for key in hittingStatsToUse:
            try:
                lgAvg = self.leagueAvgs.averages[key]
                hvp = (hs[key] + ps[key]) / 2

                if key == "BB%":
                    if hs[key] >= lgAvg:
                        self.overall += (hs[key] / lgAvg) * 1
                    if hvp >= lgAvg:
                        self.overall += (hvp / lgAvg) * 1
                elif key == "K%":
                    if hs[key] <= lgAvg:
                        self.overall += (lgAvg / hs[key]) * 1
                    else:
                        self.overall -= (hs[key] / lgAvg) * 1
                    if hvp <= lgAvg:
                        self.overall += (lgAvg / hvp) * 1
                    else:
                        self.overall -= (hvp / lgAvg) * 1
                elif key == "BABIP":
                    if hs[key] >= lgAvg:
                        self.overall += (hs[key] / lgAvg) * 1.5
                    else:
                        self.overall -= (lgAvg / hs[key]) * 1.5
                    if hvp >= lgAvg:
                        self.overall += (hvp / lgAvg) * 1.5
                    else:
                        self.overall -= (lgAvg / hvp) * 1.5
                elif key == "ISO":
                    if hs[key] >= lgAvg:
                        self.overall += (hs[key] / lgAvg) * 1.5
                    else:
                        self.overall -= (lgAvg / hs[key]) * 1.5
                    if hvp >= lgAvg:
                        self.overall += (hvp / lgAvg) * 1.5
                    else:
                        self.overall -= (lgAvg / hvp) * 1.5
                    #self.hrRating += hvp + (hvp * self.parkFactors['hr'])
                elif key == "wOBA":
                    if hs[key] >= lgAvg:
                        self.overall += (hs[key] / lgAvg) * 2
                    else:
                        self.overall -= (lgAvg / hs[key]) * 2
                    if hvp >= lgAvg:
                        self.overall += (hvp / lgAvg) * 2
                    else:
                        self.overall -= (lgAvg / hvp) * 2
            except ZeroDivisionError as e:
                print(e)

        self.applyAtBat(hs['PA'], avgPA)
        self.calcHRRating(hs, ps)

    def applyAtBat(self, hpa, avgPA): #CHANGE TO AT BAT WEIGHT
        factor = (hpa / avgPA)
        self.overall = self.overall * factor

    def calcHRRating(self, hs, ps):
        try:
            wISO = ((hs['ISO'] + ps['ISO']) / 2) / self.leagueAvgs.averages['ISO']
            wHRFB = ((hs['HR/FB'] + ps['HR/FB']) / 2) / self.leagueAvgs.averages['HR/FB']
            wHH = ((hs['Hard%'] + ps['Hard%']) / 2) / self.leagueAvgs.averages['Hard']
            self.hrRating = wISO * wHRFB * wHH * self.parkFactors['hr']
        except:
            self.hrRating = 0.0