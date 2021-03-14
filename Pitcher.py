from pybaseball import playerid_lookup
from datetime import datetime
import requests
import json
import ScraperUtils

class Pitcher:
                                                                    #id, year
    STATS_URL = "https://cdn.fangraphs.com/api/players/splits?playerid={}&position=P&season={}&split=&z=1614959387TEAM_CHANGE"

    errorLog = None
    fullName = ""
    firstName = ""
    lastName = ""
    playerId = None
    team = ""
    rawStatData = None
    weakToL = False
    weakToR = False
    ratingL = 0
    ratingR = 0
    avgRating = 0
    statYear = None
    oppTeam= ""
    scraperUtil = None
    preFormattedName = ""


    def __init__(self, name, oppTeam, team):
        self.scraperUtil = ScraperUtils.ScraperUtils()
        self.errorLog = open("PitcherErrorLog.txt", "a")
        self.statYear = datetime.now().year
        self.oppTeam = oppTeam
        self.team = team
        self.preFormattedName = name
        self.fullName = self.scraperUtil.checkForJr(name)
        self.breakUpName(name)
        self.playerId = self.scraperUtil.getFangraphsId(self.preFormattedName, self.team, self.lastName, self.firstName, self.statYear)
        if self.playerId != None:
            self.getPitcherData()
        self.errorLog.close()

    def breakUpName(self, name):
        if "Jr." in name:
            print("HAS JR.: {}".format(name))

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

    def getPitcherData(self):
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
                    print("Got stats for {} for year {}".format(self.fullName, tryYear - x))
                    break
                elif x == 2:
                    self.errorLog.write("Pitcher data for {} from url: {} not returning data".format(formattedName, url))
            except Exception as e:
                print(e)

    def calcAvgRating(self):
        self.avgRating = (self.ratingL + self.ratingR) / 2
