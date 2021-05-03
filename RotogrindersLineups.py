
from bs4 import BeautifulSoup
import requests
import datetime
import re

class RotogrindersLineups:
    URL = "https://rotogrinders.com/lineups/mlb?date={}&site=fanduel"
    weatherIcons = {
        "icn-dome": "Dome",
        "icn-sunny": "Sunny",
        "icn-cloudy": "Cloudy",
        "icn-rainy": "Rainy",
        "icn-stormy": "Stormy"
    }
    gameCards = []
    nameToAbbrev = {
        "Toronto Blue Jays": "TOR",
        "Baltimore Orioles": "BAL",
        "Tampa Bay Rays": "TBR",
        "Boston Red Sox": "BOS",
        "New York Yankees": "NYY",
        "Cleveland Indians": "CLE",
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

    def __init__(self, date = None):
        if date == None:
            dt = datetime.datetime.now()
        
            day = ""
            if dt.day < 10:
                day = "0{}".format(dt.day)
            else:
                day = dt.day

            month = ""
            if dt.month < 10:
                month = "0{}".format(dt.month)
            else:
                month = dt.month
            
            year = dt.year
            
            date = "{}-{}-{}".format(year, month, day)
        
        cards = self.makeRequest(self.URL.format(date))

        self.readData(cards)
        #for card in self.gameCards:
        #    print("{} [{}] @ {} [{}] ({}) - {} Wind: {} @ {}mph Temperature: {}* Humidity: {}%".format(card.awayTeamKey, card.awayOU, card.homeTeamKey, card.homeOU, card.gameTime, card.weatherIcon, card.windDirection, card.windSpeed, card.temperature, card.humidity))

    def makeRequest(self, url):
        data = requests.get(url)
        soup = BeautifulSoup(data.text)
        cards = soup.find_all("div", {"class": "blk crd lineup"})
        
        return cards

    def readData(self, data):
        for card in data:
            teamsSoup = card.find("div", {"class": "teams"}).find_all("span", {"class": "shrt"})
            awayTeam = teamsSoup[0].text
            homeTeam = teamsSoup[1].text

            try:
                overUnderSoup = card.find("div", {"class": "ou"}).find_all("a")
                awayOU = overUnderSoup[0].text
                homeOU = overUnderSoup[1].text
            except AttributeError:
                print("Error: OU Data not yet available for {} @ {}".format(awayTeam, homeTeam))
                awayOU = 0
                homeOU = 0

            try:
                weatherSoup = card.find("div", {"class": "weather-status"})
                weatherIcon = self.weatherIcons[weatherSoup.find("span")['class'][0]]
                gameTime = weatherSoup.find("time").text
            except:
                weatherIcon = "Dome"
                

            #WIND IS RELATIVE TO STADIUM ORIENTATION
            windDirection = None
            windSpeed = None
            humidity = None
            temperature = None
            if weatherIcon != "Dome":
                windSoup = card.find("div", {"class": "wind-status"})
                windDirectionRaw = windSoup.find("span")['class'][0]
                if "-N" in windDirectionRaw:
                    windDirection = "North"
                elif "-S" in windDirectionRaw:
                    windDirection = "South"
                elif "-E" in windDirectionRaw:
                    windDirection = "East"
                elif "-W" in windDirectionRaw:
                    windDirection = "West"

                windSpeedRaw = windSoup.find("ul", {"class": "lst stats"}).find_all("li")[0].find_all("span")[0].text
                windSpeed = re.sub("\D", "", windSpeedRaw)

                tempRaw = windSoup.find("ul", {"class": "lst stats"}).find_all("li")[0].find("span", {"class": "humidity"}).text
                temperature = re.sub("\D", "", tempRaw)

                humidityRaw = windSoup.find("ul", {"class": "lst stats"}).find("li", {"class": "humidity"}).text
                humidity = re.sub("\D", "", humidityRaw)

            awayBattingOrder = []
            battingOrderSoup = card.find("div", {"class": "blk away-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
            for player in battingOrderSoup:
                name = player.find("a", {"class": "player-popup"}).text
                awayBattingOrder.append(name)
            
            homeBattingOrder = []
            battingOrderSoup = card.find("div", {"class": "blk home-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
            for player in battingOrderSoup:
                name = player.find("a", {"class": "player-popup"}).text
                homeBattingOrder.append(name)

            gameData = {
                "awayTeam": awayTeam,
                "homeTeam": homeTeam,
                "awayBattingOrder": awayBattingOrder,
                "homeBattingOrder": homeBattingOrder,
                "awayOU": awayOU,
                "homeOU": homeOU,
                "weatherIcon": weatherIcon,
                "gameTime": gameTime,
                "windDirection": windDirection,
                "windSpeed": windSpeed,
                "humidity": humidity,
                "temperature": temperature
            }
            gCard = self.GameCards(gameData)
            self.gameCards.append(gCard)

    def getGameCard(self, teamName):
        key = self.nameToAbbrev[teamName]

        if key == "WSN":
            key = "WAS"

        for card in self.gameCards:
            if card.awayTeamKey == key or card.homeTeamKey == key:
                return card

        print("Couldn't find game card for key: {}".format(key))

    class GameCards:
        awayTeamKey = None
        homeTeamKey = None
        awayBattingOrder = []
        homeBattingOrder = []
        awayOU = None
        homeOU = None
        weatherIcon = None
        gameTime = None
        windDirection = None
        windSpeed = None
        humidity = None
        temperature = None
        battingOrder = []
        nameToAbbrev = {
            "Toronto Blue Jays": "TOR",
            "Baltimore Orioles": "BAL",
            "Tampa Bay Rays": "TBR",
            "Boston Red Sox": "BOS",
            "New York Yankees": "NYY",
            "Cleveland Indians": "CLE",
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

        def __init__(self, data):
            self.awayTeamKey = data['awayTeam']
            self.homeTeamKey = data['homeTeam']
            self.awayBattingOrder = data['awayBattingOrder']
            self.homeBattingOrder = data['homeBattingOrder']
            self.awayOU = data['awayOU']
            self.homeOU = data['homeOU']
            self.weatherIcon = data['weatherIcon']
            self.gameTime = data['gameTime']
            self.windDirection = data['windDirection']
            self.windSpeed = data['windSpeed']
            self.humidity = data['humidity']
            self.temperature = data['temperature']

        def getTeamOU(self, teamName):
            teamKey = self.nameToAbbrev[teamName]

            if self.awayTeamKey == teamKey:
                return self.awayOU
            elif self.homeTeamKey == teamKey:
                return self.homeOU
            
            return 0

        def getPlayerBattingOrder(self, playerName):
            count = 1
            for name in self.awayBattingOrder:
                if playerName == name:
                    return count
                count += 1
            
            count = 1
            for name in self.homeBattingOrder:
                if playerName == name:
                    return count
                count += 1
            
            return 0 #Not found in order