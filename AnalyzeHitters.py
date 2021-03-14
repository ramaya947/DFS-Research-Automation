import requests
from datetime import datetime
import pandas as pd
import Hitter

class AnalyzeHitters:
    TEAM_FANGRAPHS_URL = "https://www.fangraphs.com/teams/{}/stats?season={}"
    hitterNames = []
    targetedPitchers = []
    targetYear = None
    hitters = []

    def __init__(self, pitchers):
        self.targetYear = datetime.now().year
        self.targetedPitchers = pitchers
        self.getHittersData()

    def getHittersData(self):
        team = ""
        for pitcher in self.targetedPitchers:
            team = pitcher.oppTeam
            team = self.formatTeamName(team)
            url = self.TEAM_FANGRAPHS_URL.format(team, self.targetYear)
            page = requests.get(url)
            dfs = pd.read_html(page.text)
            playerTable = dfs[7]
            for row in range(len(playerTable) - 1):
                name = playerTable.at[row, "Name"]
                appearances = playerTable.at[row, "PA"]

                if appearances != 0:
                    hitter = Hitter.Hitter(name, team, pitcher)
                    self.hitters.append(hitter)

    def formatTeamName(self, teamName):

        fName = teamName.lower()

        if fName == "indians":
            fName = "cleveland"
        elif fName == "d-backs":
            fName = "diamondbacks"

        if " " in fName:
            fName = fName.replace(' ', '-')
        return fName