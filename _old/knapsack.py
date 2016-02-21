import numpy as np
import MySQLdb, csv, itertools, random
from functions import *
from openopt import *
import bottleneck


db = MySQLdb.connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()

cursor.execute("""SELECT * from ProjectionData
					WHERE salary IS NOT NULL
					AND pfp > 10
				ORDER BY pfp DESC""")
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
salary_dict, fp_dict, position_dict = {}, {}, {}
items = []
for row in data:
	player = {}
	player['name'] = row['player']
	player['position'] = row['position']
	player['salary'] = int(row['salary'])
	player['pfp'] = float(row['pfp'])
	position = row['position']
	player['u'] = 1
	for x in ['pg', 'sg', 'sf', 'pf', 'c', 'g', 'f']:
		player[x] = 0

	if position == 'PG':
		player['pg'] = 1
		player['g'] = 1
	elif position == 'SG':
		player['sg'] = 1
		player['g'] = 1
	elif position == 'SF':
		player['sf'] = 1
		player['f'] = 1
	elif position == 'PF':
		player['pf'] = 1
		player['f'] = 1
	elif position == 'C':
		player['c'] = 1
	items.append(player)

constraints = lambda values: ( 
							values['salary'] <= 50000,
							values['u'] == 8,
							values['pg'] >= 1,
							values['pg'] <= 3,
							values['sg'] >= 1,
							values['sg'] <= 3,
							values['sf'] >= 1,
							values['sf'] <= 3,
							values['pf'] >= 1,
							values['pf'] <= 3,
							values['c'] >= 1,
							values['c'] <= 2,
							values['g'] <= 4,
							values['f'] <= 4,
							)

objective = ['pfp', 1.0, 'max']
p = KSP('pfp', items, constraints = constraints)
r = p.solve('interalg', plot=0, iprint=0) 

print r.xf
projected = 0
salary = 0
for player in  r.xf:
	for row in items:
		if player == row['name']:
			projected += row['pfp']
			salary += row['salary']
print projected, salary




