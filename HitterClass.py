class HitterClass:
    pid = None
    fid = None
    name = None
    position = None
    salary = None
    FDPos = None
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
    careerMatchupStats = None
    oppMatchupStats = None
    careerOppMatchupStats = None
    gameCard = None

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

    def setOtherInformation(self, data, rgl):
        self.teamId = data['teamId']
        self.teamName = data['teamName']
        self.stadiumId = data['stadiumId']
        self.stadiumName = data['stadiumName']
        self.gameCard = rgl.getGameCard(self.teamName)

    def assessSelfV2(self, avgPA):
        ps = self.oppPitcher.stats['vsL'] if self.handedness == "L" else self.oppPitcher.stats['vsR']
        ps['ISO'] = ps['SLG'] - ps['AVG']
        hs = self.stats['vsL'] if self.oppPitcher.handedness == "L" else self.stats['vsR']

        careerPs = self.oppPitcher.stats['careerVsL'] if self.handedness == "L" else self.oppPitcher.stats['careerVsR']
        careerPs['ISO'] = ps['SLG'] - ps['AVG']
        careerHs = self.stats['careerVsL'] if self.oppPitcher.handedness == "L" else self.stats['careerVsR']

        if hs == None:
            return

        self.matchupStats = hs
        self.oppMatchupStats = ps
        self.careerMatchupStats = careerHs
        self.careerOppMatchupStats = careerPs

        #All Times 10
        #TODO: Add games OU
        self.overall = 0
        self.overall += float(self.gameCard.getTeamOU(self.teamName)) / 4.0
        #TODO: Add Recent Avg. wOBA minus league average
        #try:
        #    self.overall += (((hs['wOBA'] + ps['wOBA']) / 2) - self.leagueAvgs.averages['wOBA']) * 10
        #except:
        #    self.overall += 0
        #TODO: Add Career Avg. wOBA minus league average
        try:
            self.overall += (((careerHs['wOBA'] + careerPs['wOBA']) / 2) - self.leagueAvgs.averages['wOBA']) * 15
        except:
            self.overall += 0
        #TODO: Add Recent Avg. ISO minus league average
        #try:
        #    self.overall += (((hs['ISO'] + ps['ISO']) / 2) - self.leagueAvgs.averages['ISO']) * 10
        #except:
        #    self.overall += 0
        #TODO: Add Career Avg. ISO minus league average
        try:
            self.overall += (((careerHs['ISO'] + careerPs['ISO']) / 2) - self.leagueAvgs.averages['ISO']) * 15
        except:
            self.overall += 0
        #TODO: Minus BABIP ninus Career BABIP
        try:
            self.overall -= (hs['BABIP'] - careerHs['BABIP']) * 10
        except:
            self.overall -= 0
        #TODO: Add Recent Avg. FB% minus league average
        #try:
        #    self.overall += (((hs['FB%'] + ps['FB%']) / 2) - self.leagueAvgs.averages['FB']) * 10
        #except:
        #    self.overall += 0
        #TODO: Add Career Avg. FB% minus league average
        #try:
        #    self.overall += (((careerHs['FB%'] + careerPs['FB%']) / 2) - self.leagueAvgs.averages['FB']) * 15
        #except:
        #    self.overall += 0
        #TODO: Add Recent Avg. HR/FB minus league average
        #try:
        #    self.overall += (((hs['HR/FB'] + ps['HR/FB']) / 2) - self.leagueAvgs.averages['HR/FB']) * 10
        #except:
        #    self.overall += 0
        #TODO: Add Career Avg. HR/FB minus league average
        try:
            self.overall += (((careerHs['HR/FB'] + careerPs['HR/FB']) / 2) - self.leagueAvgs.averages['HR/FB']) * 5
        except:
            self.overall += 0

        self.calcHRRatingV2(hs, ps, careerHs, careerPs)
        self.applyAtBat(hs['PA'], avgPA)

    def assessSelf(self, avgPA):
        ps = self.oppPitcher.stats['vsL'] if self.handedness == "L" else self.oppPitcher.stats['vsR']
        ps['ISO'] = ps['SLG'] - ps['AVG']
        hs = self.stats['vsL'] if self.oppPitcher.handedness == "L" else self.stats['vsR']

        careerPs = self.oppPitcher.stats['careerVsL'] if self.handedness == "L" else self.oppPitcher.stats['careerVsR']
        careerPs['ISO'] = ps['SLG'] - ps['AVG']
        careerHs = self.stats['careerVsL'] if self.oppPitcher.handedness == "L" else self.stats['careerVsR']

        if hs == None:
            return

        self.matchupStats = hs
        self.oppMatchupStats = ps
        self.careerMatchupStats = careerHs
        self.careerOppMatchupStats = careerPs

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

        self.calcHRRating(hs, ps)
        self.applyAtBat(hs['PA'], avgPA)

    def applyAtBat(self, hpa, avgPA): #CHANGE TO AT BAT WEIGHT
        factor = (hpa / avgPA)
        self.overall = self.overall * factor
        self.hrRating = self.hrRating * factor

    def calcHRRatingV2(self, hs, ps, careerHs, careerPs):
        wISO = 0
        try:
            wISO = (((hs['ISO'] + ps['ISO']) / 2) - self.leagueAvgs.averages['ISO']) * 10
        except:
            pass
        wCarISO = 0
        try:
            wCarISO = (((careerHs['ISO'] + careerPs['ISO']) / 2) - self.leagueAvgs.averages['ISO']) * 15
        except:
            pass
        wHRFB = 0
        try:
            wHRFB = (((hs['HR/FB'] + ps['HR/FB']) / 2) - self.leagueAvgs.averages['HR/FB']) * 10
        except:
            pass
        wCarHRFB = 0
        try:
            wCarHRFB = (((careerHs['HR/FB'] + careerPs['HR/FB']) / 2) - self.leagueAvgs.averages['HR/FB']) * 15
        except:
            pass
        wFB = 0
        try:
            wFB = (((hs['FB%'] + ps['FB%']) / 2) - self.leagueAvgs.averages['FB']) * 10
        except:
            pass
        wCarFB = 0
        try:
            wCarFB = (((careerHs['FB%'] + careerPs['FB%']) / 2) - self.leagueAvgs.averages['FB']) * 15
        except:
            pass

        parkFactor = self.parkFactors['hr'] if self.parkFactors['hr'] != 0 else 1
        
        if self.gameCard.weatherIcon != "Dome":
            wind = 0
            if self.gameCard.windDirection == "North":
                wind = float(self.gameCard.windSpeed) / 10
            elif self.gameCard.windDirection == "South":
                wind = float(self.gameCard.windSpeed) / -10
            humidity = float(self.gameCard.humidity) / 100
            temperature = float(self.gameCard.temperature) / 100

            self.hrRating = (wISO + wCarISO + wHRFB + wCarHRFB + wFB + wCarFB + wind + humidity + temperature) * parkFactor
        else:
            self.hrRating = (wISO + wCarISO + wHRFB + wCarHRFB + wFB + wCarFB) * parkFactor

    def calcHRRating(self, hs, ps):
        try:
            wISO = ((hs['ISO'] + ps['ISO']) / 2) / self.leagueAvgs.averages['ISO']
            wHRFB = ((hs['HR/FB'] + ps['HR/FB']) / 2) / self.leagueAvgs.averages['HR/FB']
            wHH = ((hs['Hard%'] + ps['Hard%']) / 2) / self.leagueAvgs.averages['Hard']
            self.hrRating = wISO * wHRFB * wHH * self.parkFactors['hr']
        except:
            self.hrRating = 0.0