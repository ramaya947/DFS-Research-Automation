import ScraperUtils

name = "Tommy La Stella"
pid = 12371
s = ScraperUtils.ScraperUtils()

position = s.getPlayerPosition(name, pid)
print(position[0])