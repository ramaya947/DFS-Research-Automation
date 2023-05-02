import requests, statsapi, json

apiURL = 'http://127.0.0.1:8090/api/collections/{}/records'

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

def getAllPlayers(collection):
  response = None
  
    try:
        response = requests.get(apiURL.format(collection))

        # Request was successful, parse JSON and see if anything was found
        JSON = json.loads(response.text)
        if 'code' in JSON.keys():
            if JSON['code'] != 200:
                response = None

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
    response = getEntireSeasonsStats(collection, 'pid=\'{}\')(date=\'{}\''.format(payload['pid'], payload['date']))
    if response is not None:
        #print("Entry was already found")
        return response

    try:
        response = requests.post(apiURL.format(collection), json = payload)
    except:
        print('ERROR: Failed to add performance to PB database')
        return None
    
    return json.loads(response.text)

# Example request to getPlayer
# getPlayer('players', 'name=Shohei Ohtani', 'Shohei Ohtani')