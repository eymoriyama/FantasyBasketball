import numpy as np
import MySQLdb, csv, itertools, random
from functions import *


db = MySQLdb.connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()

cursor.execute("""SELECT * from ProjectionData
					WHERE salary IS NOT NULL
					AND ampg > 30
				ORDER BY ceiling DESC """)
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
salary_dict, fp_dict, position_dict = {}, {}, {}
bench = {'pg': [], 'sg': [], 'sf': [], 'pf': [], 'c': [], 'g': [], 'f': [], 'u': []}
for row in data:
	player = row['player_name']
	position = row['dk_position']
	salary = float(row['salary'])
	pfp = float(row['ceiling'])
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
count = 0
new_bench = bench
while True:
	for row in data:
		player = row['player_name']
		position = row['dk_position']
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

	new_bench = bench
	for position in ['pg', 'sg', 'sf', 'pf', 'c', 'g', 'f', 'u']:
		cap = len(new_bench[position]) - 1
		x = random.randint(0, cap)
		sub = new_bench[position][x]
		team[position] =  sub
		for position in list(new_bench.keys()):
			try:
				new_bench[position].remove(sub)
			except ValueError:
				pass
	
	budget = getBudget(team, salary_dict)
	fp = getTotalPoints(team, fp_dict)
	if budget <= 50000 and fp > 325:
		print tuple(team.values()), fp, budget
		count += 1

	if count == 10:
		break
	


		