import ScraperUtils, requests, pandas as pd, json

STAT_URL = "https://www.fangraphs.com/players/{}/{}/stats?"
url = STAT_URL.format("tommy-la-stella", 12371)
page = requests.get(url)
data = page.url
#data = json.loads(page.text)
print(data)