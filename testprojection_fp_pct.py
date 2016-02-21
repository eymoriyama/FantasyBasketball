import requests, json, MySQLdb, itertools, scipy, math, datetime
from datetime import timedelta
from scipy import stats
import numpy as np
from classes import *
from functions import *
from playernames import *
from city_dic import *


# UPDATES TO TABLE
db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()

actual_fp_list = []
pfp_list = []
start_date = datetime.datetime(2016, 1, 1)
for x in range(0, 50):
	cursor.execute("DELETE FROM projectiondata")
	obs_date = str(start_date + timedelta(days=x))[:10]
	
	# GAMES FOR A GIVEN NIGHT
	cursor.execute(
		"""SELECT * 
		FROM playerdata
		WHERE date(date) = '%s'
		AND played = 1
 		""" % (obs_date))
	column_names = [col[0] for col in cursor.description]
	games = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	# SALARY DATA
	cursor.execute(
	""" SELECT * FROM
		(SELECT date, player, salary
		FROM SalaryData) as a
		JOIN (SELECT player, max(date) as max_date
		FROM SalaryData 
		WHERE date(date) <= '%s'
		GROUP BY 1) as b
		ON a.date = b.max_date and a.player = b.player
	 """ % (obs_date))
	column_names = [col[0] for col in cursor.description]
	salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	# AVG FP PCT DATA
	cursor.execute(
	"""SELECT a.player, avg(fp_pct) as avg_fp_pct
	FROM (SELECT player.date, player.player, (player.fp/team.team_fp)*100 AS fp_pct 
	FROM (SELECT date, team, player, fp FROM playerdata
		WHERE played = 1
		AND date < '%s') AS player
	LEFT JOIN (SELECT date, team, sum(fp) as team_fp from playerdata GROUP BY 1, 2) AS team
	ON player.team = team.team AND player.date = team.date) AS a
	GROUP BY a.player""" % (obs_date))
	column_names = [col[0] for col in cursor.description]
	player_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	for row in games:
		player = row['player'].replace('.', '')
		team = row['team']
		starter = row['starter']
		position = row['position'].upper()
		venue = row['venue']
		opp = row['opponent']
	 	minutes_list = []
	 	starter_list = []
	 	variables = []
	 	for next_row in player_data:
	 		if player == next_row['player'].replace('.', ''):
	 			pfp = next_row['avg_fp_pct']

		# GRAB PLAYER SALARY
		salary = None
		for next_row in salary_data:
			player_name = next_row['player'].replace('.', '')
			try:
				player_name = names_dic[player_name]
			except KeyError:
				pass
			if player == player_name:
				salary = next_row['salary']

		
		cursor.executemany("INSERT INTO ProjectionData (date, team, opp, player, position, pfp, salary, starter, venue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
		[(obs_date, team, opp, player, position, pfp, salary, starter, venue)])


	cursor.execute("""SELECT * from ProjectionData
				WHERE salary IS NOT NULL
				ORDER BY (pfp/salary) DESC""")
	column_names = [col[0] for col in cursor.description]
	data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	team_dic = {'pg': '', 'sg': '', 'sf': '', 'pf': '', 'c': '', 'g': '', 'f': '', 'u': ''}
	players = []
	if data != []:
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
		team = optimizeTeam(team, players)
		optimal_team = team[0]
		budget = team[1]
		pfp = team[2]


	cursor.execute("""SELECT player, fp FROM playerdata
					WHERE date(date) = '%s'""" % (obs_date))

	column_names = [col[0] for col in cursor.description]
	data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	actual_fp = 0
	for row in data:
		if row['player'].replace('.', '') in optimal_team:
			actual_fp += row['fp']
	if data != []:		
		actual_fp_list.append(actual_fp)
		pfp_list.append(pfp)
		cursor.execute("DELETE FROM projectiondata")
		print optimal_team, pfp, actual_fp, budget, obs_date

print np.average(actual_fp_list)
print np.std(actual_fp_list)
print max(actual_fp_list)
print actual_fp_list
print pfp_list






db.commit()
db.close()
