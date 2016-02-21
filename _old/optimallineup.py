import numpy as np
import MySQLdb, csv, itertools, random
from functions import *


db = MySQLdb.connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()

cursor.execute("""SELECT * from ProjectionData
					WHERE salary IS NOT NULL
					and ampg > 20
				ORDER BY pfp DESC""")
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
salary_dict, fp_dict, position_dict = {}, {}, {}
bench = {'pg': [], 'sg': [], 'sf': [], 'pf': [], 'c': [], 'g': [], 'f': [], 'u': []}
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

count = 1
team = {}
for position in ['pg', 'sg', 'sf', 'pf', 'c', 'g', 'f', 'u']:
	sub = bench[position][0]
	team[position] = sub
	bench[position].remove(sub)

	if position_dict[sub] in ('pg', 'sg'):
		try:
			bench['g'].remove(sub)
		except ValueError:
			pass
	if position_dict[sub] in ('sf', 'pf'):
		try:
			bench['f'].remove(sub)
		except ValueError:
			pass
	try:
		bench['u'].remove(sub)
	except ValueError:
		pass

count = 0
while True:
	if getBudget(team, salary_dict) <= 50000:
		fp = getTotalPoints(team, fp_dict)
		print team, fp, getBudget(team, salary_dict)
		count += 1
		if count >= 30:
			break
	
	diff_dict = {}
	for position in list(bench.keys()):
		starter = team[position]
		sub = bench[position][0]
		fp_diff = fp_dict[starter] - fp_dict[sub]
		salary_diff = salary_dict[starter] - salary_dict[sub] 
		if salary_diff > 0:
			diff_dict[position] = fp_diff
		if salary_diff < 0:
			bench[position].remove(sub)

		
	diff_list = list(diff_dict.values())
	diff_list.sort()

	if len(diff_list) == 0:
		for position in list(bench.keys()):
			sub = bench[position][0]
			bench[position].remove(sub)
			try:
				bench['u'].remove(sub)
			except ValueError:
				pass
			if position_dict[sub] in ('pg', 'sg'):
				try:
					bench['g'].remove(sub)
				except ValueError:
					pass
			if position_dict[sub] in ('sf', 'pf'):
				try:
					bench['f'].remove(sub)
				except ValueError:
					pass

	else:
		for value in list(diff_dict.values()):
			for position in list(diff_dict.keys()):
				if diff_dict[position] == value:
					new_team = team
					new_team[position] == bench[position][0]
					if getTotalPoints(new_team, fp_dict) <= 50000:
						count += 1
						fp = getTotalPoints(new_team, fp_dict)
						print new_team, fp, getBudget(new_team, salary_dict)
						if count >= 30:
							break
				
		
		out = min(diff_dict, key=lambda k: diff_dict[k])
		sub  = bench[out][0]
		team[out] = sub
		bench[out].remove(sub)
		try:
			bench['u'].remove(sub)
		except ValueError:
			pass
		if position_dict[sub] in ('pg', 'sg'):
			try:
				bench['g'].remove(sub)
			except ValueError:
				pass
		if position_dict[sub] in ('sf', 'pf'):
			try:
				bench['f'].remove(sub)
			except ValueError:
				pass

print tuple(team.values())

		