import pandas as pd
from datetime import datetime
import requests

class TeamAverages:
    URL = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season={}&month=0&season1={}&ind=0&team=0,ts&rost=&age=&filter=&players=0"
    STATS = ["#", "Season", "G", "PA", "HR", "R", "RBI", "SB", "BB%", "K%", "ISO", "BABIP", "AVG", "OBP", "SLG", "wOBA", "wRC+", "EV", "BsR", "Off", "Def", "WAR"]
    nameToAbbrev = {
        "Blue Jays": "TOR",
        "Orioles": "BAL",
        "Rays": "TBR",
        "Red Sox": "BOS",
        "Yankees": "NYY",
        "Indians": "CLE",
        "Royals": "KCR",
        "Tigers": "DET",
        "Twins": "MIN",
        "White Sox": "CHW",
        "Angels": "LAA",
        "Astros": "HOU",
        "Athletics": "OAK",
        "Mariners": "SEA",
        "Rangers": "TEX",
        "Braves": "ATL",
        "Marlins": "MIA",
        "Mets": "NYM",
        "Nationals": "WSN",
        "Phillies": "PHI",
        "Brewers": "MIL",
        "Cardinals": "STL",
        "Cubs": "CHC",
        "Pirates": "PIT",
        "Reds": "CIN",
        "D-backs": "ARI",
        "Dodgers": "LAD",
        "Giants": "SFG",
        "Padres": "SDP",
        "Rockies": "COL"
    }
    averages = {}
    teamNameList = []
    
    def __init__(self):
        lastYear = datetime.now().year - 1
        url = self.URL.format(lastYear, lastYear)
        page = requests.get(url)
        dfs = pd.read_html(page.text)
        table = dfs[16] #May change in the future, watch out

        teamData = {}
        teamKey = ""
        for row in range(len(table) - 1):
            for col in table:
                key = col[1]
                value = table.at[row, col]

                if key == "#":
                    continue
                elif key == "Team":
                    teamKey = value
                    teamData[teamKey] = {}
                    self.teamNameList.append(teamKey)
                    continue
                if "%" in key:
                    value = float(value.strip('%')) / 100.0
                else:
                    value = float(value)
                teamData[teamKey][key] = value
        
        self.averages = teamData
    
    def getTeamKey(self, teamName):
        try:
            return self.nameToAbbrev[teamName]
        except:
            print("Could not get team stats for {}".format(teamName))