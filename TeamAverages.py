import pandas as pd
from datetime import datetime
import requests

class TeamAverages:
    URL = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=1&season={}&month={}&season1={}&ind=0&team=0,ts&rost=&age=&filter=&players=0"
    STATS = ["#", "Season", "G", "PA", "HR", "R", "RBI", "SB", "BB%", "K%", "ISO", "BABIP", "AVG", "OBP", "SLG", "wOBA", "wRC+", "EV", "BsR", "Off", "Def", "WAR"]
    SPLIT_KEY = {
        "vsL": 13,
        "vsR": 14
    }
    nameToAbbrev = {
        "Toronto Blue Jays": "TOR",
        "Baltimore Orioles": "BAL",
        "Tampa Bay Rays": "TBR",
        "Boston Red Sox": "BOS",
        "New York Yankees": "NYY",
        "Cleveland Guardians": "CLE",
        "Kansas City Royals": "KCR",
        "Detroit Tigers": "DET",
        "Minnesota Twins": "MIN",
        "Chicago White Sox": "CHW",
        "Los Angeles Angels": "LAA",
        "Houston Astros": "HOU",
        "Oakland Athletics": "OAK",
        "Seattle Mariners": "SEA",
        "Texas Rangers": "TEX",
        "Atlanta Braves": "ATL",
        "Miami Marlins": "MIA",
        "New York Mets": "NYM",
        "Washington Nationals": "WSN",
        "Philadelphia Phillies": "PHI",
        "Milwaukee Brewers": "MIL",
        "St. Louis Cardinals": "STL",
        "Chicago Cubs": "CHC",
        "Pittsburgh Pirates": "PIT",
        "Cincinnati Reds": "CIN",
        "Arizona Diamondbacks": "ARI",
        "Los Angeles Dodgers": "LAD",
        "San Francisco Giants": "SFG",
        "San Diego Padres": "SDP",
        "Colorado Rockies": "COL"
    }
    fanduelNameToAbbrev = {
        "Toronto Blue Jays": "TOR",
        "Baltimore Orioles": "BAL",
        "Tampa Bay Rays": "TB",
        "Boston Red Sox": "BOS",
        "New York Yankees": "NYY",
        "Cleveland Guardians": "CLE",
        "Kansas City Royals": "KC",
        "Detroit Tigers": "DET",
        "Minnesota Twins": "MIN",
        "Chicago White Sox": "CWS",
        "Los Angeles Angels": "LAA",
        "Houston Astros": "HOU",
        "Oakland Athletics": "OAK",
        "Seattle Mariners": "SEA",
        "Texas Rangers": "TEX",
        "Atlanta Braves": "ATL",
        "Miami Marlins": "MIA",
        "New York Mets": "NYM",
        "Washington Nationals": "WSH",
        "Philadelphia Phillies": "PHI",
        "Milwaukee Brewers": "MIL",
        "St. Louis Cardinals": "STL",
        "Chicago Cubs": "CHC",
        "Pittsburgh Pirates": "PIT",
        "Cincinnati Reds": "CIN",
        "Arizona Diamondbacks": "ARI",
        "Los Angeles Dodgers": "LAD",
        "San Francisco Giants": "SF",
        "San Diego Padres": "SD",
        "Colorado Rockies": "COL"
    }
    averages = {
        "vsL": {},
        "vsR": {}
    }
    teamNameList = []
    
    def __init__(self):
        lastYear = datetime.now().year
        url = self.URL.format(lastYear, self.SPLIT_KEY['vsL'], lastYear)
        page = requests.get(url)
        dfs = pd.read_html(page.text)
        table = dfs[5] #May change in the future, watch out
        self.getData(table, "vsL")
        
        url = self.URL.format(lastYear, self.SPLIT_KEY['vsR'], lastYear)
        page = requests.get(url)
        dfs = pd.read_html(page.text)
        table = dfs[5] #May change in the future, watch out
        self.getData(table, "vsR")

    def getData(self, table, split):
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
        
        self.averages[split] = teamData
    
    def getTeamKey(self, teamName):
        try:
            return self.nameToAbbrev[teamName]
        except:
            print("Could not get team stats for {}".format(teamName))

    def getFanduelTeamKey(self, teamName):
        try:
            return self.fanduelNameToAbbrev[teamName]
        except:
            print("Could not get team stats for {}".format(teamName))