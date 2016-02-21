import numpy as np
import MySQLdb, csv, itertools, random
from functions import *


db = MySQLdb.connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()

obs_date = '2016-01-30'
cursor.execute("""SELECT * from PlayerData
				WHERE date(date) = '%s'
				ORDER BY fp DESC""" % (obs_date))
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

### Query to get current salary for player
cursor.execute(
""" SELECT * FROM salarydata
	WHERE date(date) = '%s'""" % (obs_date))
column_names = [col[0] for col in cursor.description]
salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

for row in data:
	player = row['player_name']
	check = False
	for next_row in salary_data:
		if player == next_row['player_name']:
			row['salary'] = next_row['salary']
			check = True
	if check == False:
		row['salary'] = 0


salary_dict, fp_dict, position_dict = {}, {}, {}
bench = {'pg': [], 'sg': [], 'sf': [], 'pf': [], 'c': [], 'g': [], 'f': [], 'u': []}
for row in data:
	player = row['player_name']
	position = row['dk_position']
	salary = float(row['salary'])
	pfp = float(row['fp'])
	salary_dict[player] = salary
	fp_dict[player] = pfp
	position_dict[player] = position.lower()
	if salary != 0:
		bench['u'].append(player)
		if position == 'PG':
			bench['pg'].append(player)
			bench['g'].append(player)
		if position == 'SG':
			bench['sg'].append(player)
			bench['g'].append(player)
		if position == 'SF':
			bench['sf'].append(player)
			bench['f'].append(player)
		if position == 'PF':
			bench['pf'].append(player)
			bench['f'].append(player)
		if position == 'C':
			bench['c'].append(player)

count = 1
team = {}
for position in ['pg', 'sg', 'sf', 'pf', 'c', 'g', 'f', 'u']:
	sub = bench[position][0]
	team[position] = sub
	for row in list(bench.keys()):
		try:
			bench[row].remove(sub)
		except ValueError:
			pass	


team = getOptimalTeamv2(team, bench, salary_dict, fp_dict)
print team['team'], team['pfp']



