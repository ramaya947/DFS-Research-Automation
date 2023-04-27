import json

data = json.load(open('./model/constants/RequestBodys.JSON', 'r'))
data['datedPlayerSplitsStats']['strPlayerId'] = "poop"

print(data)