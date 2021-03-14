from pybaseball import playerid_lookup
import csv, urllib.parse as urlparse, requests
from urllib.parse import parse_qs

class ScraperUtils:
    GET_POS_URL = "https://www.fangraphs.com/players/{}/{}/stats?"

    def __init__(self):
        pass

    def getFangraphsId(self, fullName, team, last, first, statYear):
        #Grab player id from register
        last = last.lower()
        first = first.lower()
        #If player name has '.' in it, remove
        if '.' in last:
            last = last.replace('.', '. ', 1)
        if '.' in first:
            first = first.replace('.', '. ', 1)

        last = last.strip()
        first = first.strip()

        try:
            playerList = playerid_lookup(last, first)
            for row in range(len(playerList)):
                lastYearPlayed = playerList.at[row, "mlb_played_last"]
                if lastYearPlayed == statYear or lastYearPlayed == (statYear - 1):
                    playerId = playerList.at[row, "key_fangraphs"]
                    return playerId
            playerId = self.checkInCsvRecords(fullName, team)
            if playerId == None:
                raise Exception("No Matching player found for [{}] [{}]".format(first, last))
            else:
                return playerId
        except Exception as e:
            playerId = None
            p = playerid_lookup(last)
            print(e)
            #print(p)
            return playerId

    def getPlayerPosition(self, fullName, playerId):
        formattedName = fullName.replace(' ', '-')
        formattedName = formattedName.lower()
        url = self.GET_POS_URL.format(formattedName, playerid_lookup)
        page = requests.get(url)
        newUrl = page.url
        print(newUrl)
        parsed = urlparse.urlparse(newUrl)
        position = parse_qs(parsed.query)["position"]
        return position

    def checkForJr(self, string):
        temp = string
        if "Jr." in temp:
            temp = temp.replace("Jr.", '')
            temp = temp.strip()

        return temp

    def checkInCsvRecords(self, fullName, team):
        file = open("MissingPlayerIds.csv")
        csv_reader = csv.reader(file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                if row[0] == fullName and row[1] == team:
                    playerId = row[2]
                    file.close()
                    return playerId
                
            line_count += 1
        
        #Player Not Found
        file.close()
        file = open("MissingPlayerIds.csv", "a")
        file.write("{},{},\n".format(fullName, team))
        file.close()
