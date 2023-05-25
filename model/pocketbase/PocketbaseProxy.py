import requests, statsapi, json
from unidecode import unidecode

FANGRAPHS_SEARCH_URL = "https://85798c555f18463c9d3ec7d18778c367.ent-search.us-east1.gcp.elastic-cloud.com/api/as/v1/engines/fangraphs/search.json"
apiURL = 'http://127.0.0.1:8090/api/collections/{}/records'

def searchForFangraphsId(name, narrowingFields = []):
    requestHeaders = {
        "Authorization": "Bearer search-cty1wzhqd1pqueai45ccxh7y"
    }

    body = {
        "query": name,
        "search_fields": {
            "name": {},
            "namekorean": {}
        },
        "result_fields": {
            "id": {
                "raw": {}
            },
            "name": {
                "raw": {}
            }
        }
    }

    response = requests.post(url= FANGRAPHS_SEARCH_URL, headers = requestHeaders, json = body)
    data = json.loads(response.text)
    
    # Match the name
    matches = []
    for player in data['results']:
        if name in unidecode(player['name']['raw']):
            matches.append({
                'id': player['id']['raw'],
                'name': name
            })

    if len(narrowingFields) == 0 and len(matches) != 0:
        return matches[0]
    
    # Do the narrowing
    return {}

def checkStatsAPI(name):
    if name == None:
        print('No passed in name, cannot check statsapi')
        return None
    
    player = statsapi.lookup_player(name)
    if (len(player) > 0):
        return player[0]
    else:
        return None

def updatePlayer(collection, pbId, payload):
    response = None

    try:
        response = requests.patch(apiURL.format(collection) + '/{}'.format(pbId), json = payload)
    except:
        print('ERROR: Failed to updated player in PB database')

    return json.loads(response.text)

def addPlayer(collection, payload):
    response = None

    try:
        response = requests.post(apiURL.format(collection), json = payload)
    except:
        print('ERROR: Failed to add player to PB database')
    
    return json.loads(response.text)

def getPlayer(collection, queryParams, name = None):
    response = None

    try:
        response = requests.get(apiURL.format(collection) + '?filter=({})'.format(queryParams))

        # Request was successful, parse JSON and see if anything was found
        JSON = json.loads(response.text)
        if 'code' in JSON.keys():
            if JSON['code'] != 200:
                response = None

    except:
        print('ERROR: PB request failed')

    if response == None:
        # Databse request failed, check statsapi
            player = checkStatsAPI(name)

            if player == None:
                print('Player not found')
                return None
            
            # TODO: Before adding to database, check that the pid is not in the database already
            # There is an issue with multiple entries being in the database
            response = requests.get(apiURL.format(collection) + '?filter=({})'.format('pid={}'.format(player['id'])))

            JSON = json.loads(response.text)
            if JSON['totalItems'] != 0:
                response = JSON['items'][0]
                print('Found player by pid instead of name. Given: {} vs Found: {}'.format(name, response['name']))
                return response

            # Add to PB database
            payload = { 'pid': player['id'], 'name': name}
            response = addPlayer(collection, payload)
            return response
    else:
        if  JSON['totalItems'] != 0:
            response = JSON['items'][0]
            return response
        else:
            # Player not found in PB database, check statsapi
            player = checkStatsAPI(name)

            if player == None:
                print('Player not found')
                return None
            
            # TODO: Before adding to database, check that the pid is not in the database already
            # There is an issue with multiple entries being in the database
            response = requests.get(apiURL.format(collection) + '?filter=({})'.format('pid={}'.format(player['id'])))

            JSON = json.loads(response.text)
            if JSON['totalItems'] != 0:
                response = JSON['items'][0]
                print('Found player by pid instead of name. Given: {} vs Found: {}'.format(name, response['name']))
                return response

            # Add to PB database
            payload = { 'pid': player['id'], 'name': name}
            response = addPlayer(collection, payload)
            return response

def getPlayerViaFangraphs(collection, queryParams, name = None):
    response = None

    response = requests.get(apiURL.format(collection) + '?filter=({})'.format(queryParams))

    # Request was successful, parse JSON and see if anything was found
    JSON = json.loads(response.text)
    if 'code' in JSON.keys():
        if JSON['code'] != 200:
            response = None

    if response != None and JSON['totalItems'] != 0:
        response = JSON['items'][0]
        return response
    
    fangraphsResponse = searchForFangraphsId(name)

    if 'id' not in fangraphsResponse:
        return None

    # Add to PB database
    payload = { 'fid': fangraphsResponse['id'], 'name': name }
    response = addPlayer(collection, payload)

    return response

def getAllPlayers(collection):
    response = None
  
    try:
        response = requests.get(apiURL.format(collection) + '?perPage=1000')

        # Request was successful, parse JSON and see if anything was found
        JSON = json.loads(response.text)
        if 'code' in JSON.keys():
            if JSON['code'] != 200:
                response = None
                return response
        return JSON['items']

    except:
        print('ERROR: PB request failed')
        return response

def getEntireSeasonsStats(collection, queryParams):
    response = None

    try:
        response = requests.get(apiURL.format(collection) + '?filter=({})'.format(queryParams))

        # Request was successful, parse JSON and see if anything was found
        JSON = json.loads(response.text)
        if 'code' in JSON.keys():
            if JSON['code'] != 200:
                response = None
        return JSON['items'][0]
    except:
        #print('ERROR: PB request failed')
        return None

def addEntireSeasonsStats(collection, payload):
    response = None
    
    # Check that record is not already there
    response = getEntireSeasonsStats(collection, 'pid=\'{}\')(season={})(type={}'.format(payload['pid'], payload['season'], payload['type']))
    if response is not None:
        #print("Entry was already found")
        return response

    try:
        response = requests.post(apiURL.format(collection), json = payload)
    except:
        print('ERROR: Failed to add stats to PB database')
        return None
    
    return json.loads(response.text)

def addPerformanceRecord(collection, payload):
    response = None
    
    # Check that record is not already there
    response = getEntireSeasonsStats(collection, 'fid=\'{}\')(date=\'{}\''.format(payload['fid'], payload['date']))
    if response is not None:
        #print("Entry was already found")
        return response

    try:
        response = requests.post(apiURL.format(collection), json = payload)
    except:
        print('ERROR: Failed to add performance to PB database')
        return None
    
    return json.loads(response.text)

def getAllPerformanceRecords(collection, queryParams):
    response = None

    try:
        response = requests.get(apiURL.format(collection) + '?filter=({})'.format(queryParams))

        # Request was successful, parse JSON and see if anything was found
        JSON = json.loads(response.text)
        if 'code' in JSON.keys():
            if JSON['code'] != 200:
                response = None
        return JSON['items']
    except:
        #print('ERROR: PB request failed')
        return None
    
def addRValue(collection, payload):
    response = None

    try:
        response = requests.post(apiURL.format(collection), json = payload)
    except:
        print('ERROR: Failed to add rValue to PB database')
    
    return json.loads(response.text)

def getRValue(collection, queryParams):
    response = None

    response = requests.get(apiURL.format(collection) + '?filter=({})'.format(queryParams))

    # Request was successful, parse JSON and see if anything was found
    JSON = json.loads(response.text)
    if 'code' in JSON.keys():
        if JSON['code'] != 200:
            response = None

    if response != None and JSON['totalItems'] != 0:
        response = JSON['items'][0]
        return response
    
    return None

# Example request to getPlayer
# getPlayer('players', 'name=Shohei Ohtani', 'Shohei Ohtani')
#playerName = "Jazz Chisholm"
#getPlayerViaFangraphs('players', 'name=\'{}\''.format(playerName), playerName)