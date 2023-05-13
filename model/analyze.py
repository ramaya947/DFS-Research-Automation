import pocketbase.PocketbaseProxy as pocketbase
from openpyxl import Workbook, utils

# TODO: Call getAllPlayers
players = pocketbase.getAllPlayers('players')

wb = Workbook()

# TODO: Create workbook sheets for all positions
positions = ['P', 'C', '1B', '2B', '3B', 'SS', 'OF']
dict = {}
for pos in positions:
	dict[pos] = {
		'sheet': wb.create_sheet(pos),
		'hasHeaders': False
	}

count = 0
for player in players:
	performances = pocketbase.getAllPerformanceRecords('performances', 'pid=\'{}\''.format(player['pid']))
	
	try:
		prevSeasonStats = {
			'standard': pocketbase.getEntireSeasonsStats('seasonStats', 'pid=\'{}\')(season={})(type={}'.format(player['pid'], 2021, 1))['stats'],
			'advanced': pocketbase.getEntireSeasonsStats('seasonStats', 'pid=\'{}\')(season={})(type={}'.format(player['pid'], 2021, 2))['stats'],
			'battedBall': pocketbase.getEntireSeasonsStats('seasonStats', 'pid=\'{}\')(season={})(type={}'.format(player['pid'], 2021, 3))['stats']
		}
	except:
		count += 1
		continue

	if (
		len(prevSeasonStats['standard']) == 0 or
		len(prevSeasonStats['advanced']) == 0 or
		len(prevSeasonStats['battedBall']) == 0
	):
		count += 1
		continue

	for performance in performances:
		positions = performance['positions'].split('/')
		sheets = []
		for pos in positions:
			sheets.append(dict[pos])

		headerRow = []
		statRow = []
		# Add all headers if needed, add stats for prev Year
		for key in prevSeasonStats.keys():
			stats = prevSeasonStats[key]
			for statDict in stats:
				for stat in statDict.keys():
					if isinstance(statDict[stat], str) or stat == 'Season':
						continue
					headerRow.append('prevSeason-{}-{}'.format(key, stat))
					statRow.append(statDict[stat])
		# Add all headers if needed, add stats for performance
		performanceStats = {
			'standardCurrentSeason': performance['standardCurrSeasonStats'],
			'advancedCurrentSeason': performance['advancedCurrSeasonStats'],
			'battedBallCurrentSeason': performance['battedBallCurrSeasonStats'],
			'standardLastWeek': performance['standardLastWeekStats'],
			'advancedLastWeek': performance['advancedLastWeekStats'],
			'battedBallLastWeek': performance['battedBallLastWeekStats'],
			'standardTwoWeek': performance['standardTwoWeekStats'],
			'advancedTwoWeek': performance['advancedTwoWeekStats'],
			'battedBallTwoWeek': performance['battedBallTwoWeekStats']
		}
		for key in performanceStats.keys():
			stats = performanceStats[key]
			for statDict in stats:
				for stat in statDict.keys():
					if isinstance(statDict[stat], str) or stat == 'Season':
						continue
					headerRow.append('performance-{}-{}'.format(key, stat))
					statRow.append(statDict[stat])

		headerRow.append('FPTS')
		if not isinstance(performance['fpts'], int):
			continue
		statRow.append(performance['fpts'])
		for sheet in sheets:
			# After first pass through a performance, headers should be added and can be set to True
			if not sheet['hasHeaders']:
				sheet['sheet'].append(headerRow)
				sheet['hasHeaders'] = True

			sheet['sheet'].append(statRow)

	count += 1
	print('Player {} out of {}'.format(count + 1, len(players)), flush=True)
wb.remove_sheet(wb.get_sheet_by_name('Sheet'))
wb.save("Analysis.xlsx")