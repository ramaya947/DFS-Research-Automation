import eventlet
import statsapi, StatWrapper as sw, requests, json, datetime
from pybaseball import playerid_reverse_lookup, cache, playerid_lookup
from dateutil import tz
import LeagueAverages
from waiting import wait

class Test:

    response = None
    sio = None

    def __init__(self):
        pass

    def setResponse(self, r):
        self.response = r

    def waitingFunc(self):
        if self.response != None:
            return True
        
        return False

    def setSio(self, socket):
        global sio
        sio = socket

    def testWait(self, sio):
        print('A')

        sio.emit('Message to Client', { "message": "How much wood would a wood chuck chuck?", "isQuestion": "true"})
        while (self.response == None):
            eventlet.sleep(1)
        
        print('B')

    def askQuestion(self, question):
        global sio

        sio.emit('Message to Client', { "message": question, "isQuestion": "true"})
        while (self.response == None):
            eventlet.sleep(1)

        userResp = self.response
        self.response = None

        return userResp

    def run(self):
        cache.enable()
        manualFill = True

        hour = self.askQuestion("Please provide the hour of the slate's start time")
        minute = self.askQuestion("Please provide the minute of the slate's start time")
        compare = self.askQuestion("Does the slate start before or after the given time? (before/after)")
        
        year = datetime.date.today().year
        month = datetime.date.today().month
        day = datetime.date.today().day
        slateStart = datetime.datetime(year, month, day, int(hour), int(minute), 0)

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
        
        date = "{}/{}/{}".format(month, day, year)

        #sw.setSocket(socket)
        sw.setAskQuestionCallback(self.askQuestion)

        games = sw.getDaysGames(manualFill, slateStart, compare, False, date)
        pitchers = []
        hitters = []
        for game in games:
            sw.getGamesProbablePitchers(game, pitchers)

        sw.assessPitchers(pitchers)
        pitchers.sort(key=lambda x: x.overall, reverse=True)

        for pitcher in pitchers:
            sw.createHitters(pitcher, hitters)
            print("{} is facing off against the {} [ {} ]".format(pitcher.name, pitcher.oppTeamName, round(pitcher.overall, 2)))
            print("Total Innings Pitched: {}".format(pitcher.stats['vsL']['IP'] + pitcher.stats['vsR']['IP']))

        sw.assessHitters(hitters)

        hitters.sort(key=lambda x: x.overall, reverse=True)

        hitters = sw.getPlayerSalaries(hitters)

        players = {"C": [], "1B": [], "2B": [], "3B": [], "SS": [], "OF": []}
        for hitter in hitters:
            #print("({}) {} [ {} ]".format(hitter.position, hitter.name, hitter.overall))
            try:
                players[hitter.position].append(hitter)
            except Exception as e:
                print(e)
        
        pitchers = sw.getPlayerSalaries(pitchers)

        hitters.sort(key=lambda x: x.hrRating, reverse=True)
        sw.writeSummary(players, pitchers, hitters)
        sw.writeSummaryToCSV(players, pitchers)
        sw.cleanUp()

    def runManually(self, manualfill, slateStart, date, compare):
        cache.enable()
        
        games = sw.getDaysGames(manualFill, slateStart, compare, False, date)
        pitchers = []
        hitters = []
        for game in games:
            sw.getGamesProbablePitchers(game, pitchers)

        sw.assessPitchers(pitchers)
        pitchers.sort(key=lambda x: x.overall, reverse=True)

        for pitcher in pitchers:
            sw.createHitters(pitcher, hitters)
            print("{} is facing off against the {} [ {} ]".format(pitcher.name, pitcher.oppTeamName, round(pitcher.overall, 2)))
            print("Total Innings Pitched: {}".format(pitcher.stats['vsL']['IP'] + pitcher.stats['vsR']['IP']))

        sw.assessHitters(hitters)

        hitters.sort(key=lambda x: x.overall, reverse=True)

        hitters = sw.getPlayerSalaries(hitters)

        players = {"C": [], "1B": [], "2B": [], "3B": [], "SS": [], "OF": []}
        for hitter in hitters:
            #print("({}) {} [ {} ]".format(hitter.position, hitter.name, hitter.overall))
            try:
                players[hitter.position].append(hitter)
            except Exception as e:
                print(e)
        
        pitchers = sw.getPlayerSalaries(pitchers)

        hitters.sort(key=lambda x: x.hrRating, reverse=True)
        sw.writeSummary(players, pitchers, hitters)
        sw.writeSummaryToCSV(players, pitchers)
        sw.cleanUp()

manualFill = True
ss = datetime.datetime(2021, 6, 15, 19, 0, 0)
date = "06/15/2021"
Test().runManually(manualFill, ss, date, "after")