from bs4 import BeautifulSoup
import requests, statsapi
import pocketbase.PocketbaseProxy as pocketbase
from pybaseball import playerid_reverse_lookup
#import StatWrapper as sw


# POC
# Grab the stats for Mike Trout for the second game of last season
#   This means:
#       - Career stats for time period prior to that game
#       - Season stats up to that date
# The date was 2022-04-08

# First: Grab his total points for that day
url = "https://rotogrinders.com/lineups/mlb?date={}&site=fanduel"
date = "2022-04-08"
formattedUrl = url.format(date)

# Make request
data = requests.get(formattedUrl)
soup = BeautifulSoup(data.text)
cards = soup.find_all("div", {"class": "blk crd lineup"})

#Find all the players for that day
for card in cards:
    teamsSoup = card.find("div", {"class": "teams"}).find_all("span", {"class": "shrt"})
    awayTeam = teamsSoup[0].text
    homeTeam = teamsSoup[1].text

    players = []
    battingOrderSoup = card.find("div", {"class": "blk away-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
    for player in battingOrderSoup:
        name = player.find("a", {"class": "player-popup"}).text
        players.append(name)
    
    battingOrderSoup = card.find("div", {"class": "blk home-team"}).find("ul", {"class": "players"}).find_all("li", {"class": "player"})
    for player in battingOrderSoup:
        name = player.find("a", {"class": "player-popup"}).text
        players.append(name)

    for player in players:
        playerSoup = soup.find("a", {"title": "{}".format(player)})
        fpts = playerSoup.parent.parent.find("span", {"title": "Fantasy Points"}).text
        if fpts and fpts != None and fpts != "" and fpts != "" and fpts != '':
            print("{}: {}".format(player, fpts))
            playerInfo = pocketbase.getPlayer('players', 'name=\'{}\''.format(player), player)
            try:
                playerId = playerInfo['pid']
            except:
                print('ERROR: Could not find id for {} in returned Data: {}'.format(player, playerInfo))
                continue

            if playerInfo['fid'] == '':
                data = playerid_reverse_lookup([int(playerId)], "mlbam")

                fid = None
                try:
                    fid = data.at[0, "key_fangraphs"]
                except Exception as e: print(e)

                playerInfo = pocketbase.updatePlayer('players', playerInfo['id'], { 'fid': '{}'.format(fid) })
                print('Update entry for {}. FID is now {}'.format(player, playerInfo['fid']))
            