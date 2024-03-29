import pandas as pd
from datetime import datetime
import requests

class LeagueAverages:
    URL = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season={}&month=0&season1={}&ind=0&team=0,ss&rost=0&players=0&sort=0,d"
    STATS = ["#", "Season", "TG", "G", "PA", "HR", "R", "RBI", "SB", "BB%", "K%", "ISO", "BABIP", "AVG", "OBP", "SLG", "wOBA", "xwOBA", "wRC+", "BsR", "Off", "Def", "WAR"]
    averages = {
        "LD": .216,
        "FB": .357,
        "HR/FB": .148,
        "Hard": .333
    }
    
    def __init__(self):
        lastYear = datetime.now().year
        url = self.URL.format(lastYear, lastYear)
        page = requests.get(url)
        dfs = pd.read_html(page.text)
        table = dfs[5] #May change in the future, watch out
        count = 0
        for x in table:
            value = table.at[0,x]
            if self.STATS[count] == "BB%" or self.STATS[count] == "K%":
                value = float(value.strip('%')) / 100.0
            else:
                value = float(value)
            self.averages[self.STATS[count]] = value
            count += 1