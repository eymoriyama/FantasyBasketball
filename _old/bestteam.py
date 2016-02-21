import numpy as np
import MySQLdb, csv, itertools, random
from functions import *


db = MySQLdb.connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()

cursor.execute("""SELECT * from ProjectionData
					WHERE salary IS NOT NULL
				ORDER BY pfp DESC""")
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
salary_dict, fp_dict, position_dict = {}, {}, {}
bench = {'pg': [], 'sg': [], 'sf': [], 'pf': [], 'c': [], 'g': [], 'f': [], 'u': []}
reserves = {'pg': [], 'sg': [], 'sf': [], 'pf': [], 'c': [], 'g': [], 'f': [], 'u': []}
for row in data:
	player = row['player']
	position = row['position']
	salary = float(row['salary'])
	pfp = float(row['pfp'])
	salary_dict[player] = salary
	fp_dict[player] = pfp
	position_dict[player] = position.lower()
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
print team['team'], team['pfp'], team['budget']



