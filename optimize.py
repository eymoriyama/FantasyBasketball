import numpy as np
import MySQLdb, csv, itertools, random
from functions import *
from classes import *

db = MySQLdb.connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()

cursor.execute("""SELECT * from ProjectionData
				WHERE salary IS NOT NULL
				ORDER BY (pfp/salary) DESC""")
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
team_dic = {'pg': '', 'sg': '', 'sf': '', 'pf': '', 'c': '', 'g': '', 'f': '', 'u': ''}
players = []

for row in data:
	player_name = row['player']
	position = row['position'].lower()
	salary = float(row['salary'])
	pfp = float(row['pfp'])
	value = (pfp / salary) * 1000
	player = Player(position, player_name, salary, pfp, value)
	players.append(player)
	for position in list(team_dic.keys()):
		if team_dic[position] == '' and player not in team_dic.values():
			if player.position == position or player.second_position == position or player.third_position == position:
				team_dic[position] = player
team = Team(team_dic)
print optimizeTeam(team, players)



