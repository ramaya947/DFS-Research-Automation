from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
import pandas as pd
from openpyxl import Workbook

def analyze():
    wb = Workbook()
    hitterSheetKeys = ['C', '1B', '2B', '3B', 'SS', 'OF']
    excelData = None

    namesToScores = getNamesToScores()

    for key in hitterSheetKeys:
        sheet = wb.create_sheet(key)
        excelData = pd.read_excel('SummaryLast.xlsx', sheet_name=key)
        namesToCheck = excelData['Name'].tolist()
        overalls = excelData['Overall'].tolist()
        overUnders = excelData['OU'].tolist()

        header = ["OU", "Name", "Overall", "Points"]
        sheet.append(header)

        count = 0
        for name in namesToCheck:
            dataRow = []

            score = None
            try:
                score = namesToScores[name]
            except:
                count += 1
                continue

            dataRow.append(overUnders[count])
            dataRow.append(name)
            dataRow.append(overalls[count])
            dataRow.append(score)
            sheet.append(dataRow)

            count += 1
    
    wb.save("SummaryAnalyzed.xlsx")

def getNamesToScores():
    URL = "https://rotogrinders.com/lineups/mlb?date={}&site=fanduel"
    url = URL.format(getDate())
    scores = {}

    data = requests.get(url)
    soup = BeautifulSoup(data.text)
    cards = soup.find_all("div", {"class": "blk crd lineup"})

    for card in cards:
        playerListSoups = card.find_all("li", {"class": "player"})
        for playerSoup in playerListSoups:
            infoSoup = playerSoup.find("div", {"class": "info"})
            name = infoSoup.find("a", {"class": "player-popup"}).text
            score = infoSoup.find("span", {"class": "fpts actual"}).text

            scores[name] = score

    return scores

def getDate():
    dt = datetime.now() + timedelta(days=-1)

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

    return date

analyze()