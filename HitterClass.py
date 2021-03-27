class HitterClass:
    pid = None
    fid = None
    name = None
    position = None
    handedness = None
    oppPitcher = None
    teamId = None
    teamName = None
    stadiumId = None
    stadiumName = None
    stats = None
    overall = None
    leagueAvgs = None

    def __init__(self, data, leagueAvgs, pitcher):
        self.pid = data['person']['id']
        self.name = data['person']['fullName']
        self.position = data['position']['abbreviation']
        self.leagueAvgs = leagueAvgs
        self.overall = 0.0
        self.stats = {}
        self.oppPitcher = pitcher

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


    def applyAtBat(self, hpa, avgPA): #CHANGE TO AT BAT WEIGHT
        factor = (hpa / avgPA)
        self.overall = self.overall * factor