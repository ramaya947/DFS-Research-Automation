from openpyxl import Workbook, utils
import pocketbase.PocketbaseProxy as pocketbase, csv

# TODO: Call getAllPlayers
players = pocketbase.getAllPlayers('players')

wb = Workbook()

# TODO: Create workbook sheets for all positions
positions = ['P', 'C', '1B', '2B', '3B', 'SS', 'OF']
dict = {}
for pos in positions:
  dict[pos] = wb.create_sheet(pos)
  
pitcherSheet = wb.create_sheet("Pitchers")
sheet.append(appendRow)