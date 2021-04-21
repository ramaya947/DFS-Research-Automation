
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
        for card in self.gameCards:
            print("{} [{}] @ {} [{}] ({}) - {} Wind: {} @ {}mph Temperature: {}* Humidity: {}%".format(card.awayTeamKey, card.awayOU, card.homeTeamKey, card.homeOU, card.gameTime, card.weatherIcon, card.windDirection, card.windSpeed, card.temperature, card.humidity))

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

            overUnderSoup = card.find("div", {"class": "ou"}).find_all("a")
            awayOU = overUnderSoup[0].text
            homeOU = overUnderSoup[1].text

            weatherSoup = card.find("div", {"class": "weather-status"})
            weatherIcon = self.weatherIcons[weatherSoup.find("span")['class'][0]]
            gameTime = weatherSoup.find("time").text

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

            gameData = {
                "awayTeam": awayTeam,
                "homeTeam": homeTeam,
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

    class GameCards:
        awayTeamKey = None
        homeTeamKey = None
        awayOU = None
        homeOU = None
        weatherIcon = None
        gameTime = None
        windDirection = None
        windSpeed = None
        humidity = None
        temperature = None

        def __init__(self, data):
            self.awayTeamKey = data['awayTeam']
            self.homeTeamKey = data['homeTeam']
            self.awayOU = data['awayOU']
            self.homeOU = data['homeOU']
            self.weatherIcon = data['weatherIcon']
            self.gameTime = data['gameTime']
            self.windDirection = data['windDirection']
            self.windSpeed = data['windSpeed']
            self.humidity = data['humidity']
            self.temperature = data['temperature']

rgl = RotogrindersLineups()