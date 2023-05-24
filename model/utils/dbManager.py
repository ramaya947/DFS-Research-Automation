import requests, json

apiURL = 'http://127.0.0.1:8090/api/collections/{}/records'

def deleteAllRecords(collection):
    response = None
    records = None
  
    # Retrieve all records
    try:
        response = requests.get(apiURL.format(collection) + '?perPage=15000')

        # Request was successful, parse JSON and see if anything was found
        JSON = json.loads(response.text)
        if 'code' in JSON.keys():
            if JSON['code'] != 200:
                response = None
                return response
        records = JSON['items']

    except:
        print('ERROR: PB request failed to retrieve records')
        records = []

    if len(records) == 0:
        return

    # Delete all records
    try:
        for record in records:
            id = record['id']
            response = requests.delete(apiURL.format(collection) + '/{}'.format(id))
    except:
        print('ERROR: PB request failed to delete records')
        return
    
    print('Successfully deleted {} records'.format(len(records)))
    return deleteAllRecords(collection)

deleteAllRecords('seasonStats')
deleteAllRecords('performances')
#deleteAllRecords('players')