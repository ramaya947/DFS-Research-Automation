from pybaseball import playerid_lookup
from datetime import datetime
import requests, json
import ScraperUtils

class Hitter:
    STAT_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position=P&season={}&split=&z=1614959387TEAM_CHANGE"
    fullName = ""
    firstName = ""
    lastName = ""
    playerId = None
    team = ""
    rawStatData = None
    statYear = None
    oppPitcher = None
    rating = None
    scraperUtil = None
    preFormattedName = ""

    def __init__(self, name, team, oppPitcher):
        self.scraperUtil = ScraperUtils.ScraperUtils()
        self.statYear = datetime.now().year
        self.team = team
        self.oppPitcher = oppPitcher
        self.preFormattedName = name
        self.fullName = self.scraperUtil.checkForJr(name)
        self.breakUpName(self.fullName)
        self.playerId = self.scraperUtil.getFangraphsId(self.preFormattedName, self.team, self.lastName, self.firstName, self.statYear)
        if self.playerId != None:
            #self.getHitterData()
            pass

    def getHitterData(self):
        formattedName = self.fullName.replace(' ', '-').lower()
        tryYear = self.statYear
        for x in range(0,3):
            #' - x' to check stats at most 1 year in the past if can't find anything
            url = self.STATS_URL.format(self.playerId, tryYear - x)
            page = requests.get(url)
            data = json.loads(page.text)
            try:
                if len(data) != 0:
                    self.rawStatData = data
                    break
                elif x == 2:
                    self.errorLog.write("Pitcher data for {} from url: {} not returning data".format(formattedName, url))
                else:
                    print("Could not get stats for {} for year {}".format(self.fullName, tryYear - x))
            except Exception as e:
                print(e)

    def getFanduelPrice(self):
        pass

    def breakUpName(self, name):
        if name.count(' ') > 1:
            charCount = 0
            temp = ""
            for c in name:
                if charCount == 1 and c == ' ':
                    self.firstName = temp
                    temp = ""
                    charCount += 1
                    continue
                if c == ' ':
                    charCount += 1
                temp += c
                
            self.lastName = temp
        else:
            splitName = name.split(' ')
            self.firstName = splitName[0]
            self.lastName = splitName[1]