class PitcherClass:
    pid = None
    name = None
    position = None
    handedness = None
    oppTeamId = None
    oppTeamName = None
    teamId = None
    teamName = None
    stadiumId = None
    stadiumName = None
    stats = None
    overall = None
    ratingL = None
    ratingR = None

    def __init__(self, data):
        self.pid = data['person']['id']
        self.name = data['person']['fullName']
        self.position = data['position']['abbreviation']

    def setOtherInformation(self, data):
        self.oppTeamId = data['oppTeamId']
        self.oppTeamName = data['oppTeamName']
        self.teamId = data['teamId']
        self.teamName = data['teamName']
        self.stadiumId = data['stadiumId']
        self.stadiumName = data['stadiumName']
