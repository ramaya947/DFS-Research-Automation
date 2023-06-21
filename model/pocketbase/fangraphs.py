import requests, json
from unidecode import unidecode

FANGRAPHS_SEARCH_URL = "https://85798c555f18463c9d3ec7d18778c367.ent-search.us-east1.gcp.elastic-cloud.com/api/as/v1/engines/fangraphs/search.json"

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