import requests, json, MySQLdb, itertools, scipy, math, datetime
from datetime import timedelta
from scipy import stats
from sklearn import linear_model
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from classes import *
from functions import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()
cursor.execute("DELETE FROM TestProjection")

### Query to get points allowed per position
cursor.execute(
"""SELECT teams.opponent_name, players.dk_position, 
		sum(teams.act_fp), sum(players.exp_fp),
		 sum(teams.act_fp)/sum(players.exp_fp) as weight
	FROM (SELECT date, team_name, opponent_name, player_name, dk_position, sum(fp) as act_fp
			FROM PlayerData
			WHERE dk_position IS NOT NULL
			GROUP BY 1, 2, 3, 4, 5) as teams
	LEFT JOIN (SELECT player_name, dk_position, avg(fp) as exp_fp
				FROM PlayerData
				WHERE dk_position IS NOT NULL
				GROUP BY 1) as players
				ON teams.dk_position = players.dk_position AND teams.player_name = players.player_name
				GROUP BY 1, 2 """)
column_names = [col[0] for col in cursor.description]
opponent_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]



outliers = []
actual_fp_list = []
pfp_list = []
start_date = datetime.datetime(2016, 1, 1)
for x in range(0, 36):
	obs_date = str(start_date + timedelta(days=x))[:10]

	cursor.execute(
	"""	SELECT team_name, dk_position, avg(plus_minus) as plus_minus
		FROM playerdata 
		WHERE date(date) < '%s'
		GROUP BY 1, 2 """ % (obs_date))
		
	column_names = [col[0] for col in cursor.description]
	plus_minus_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	
	cursor.execute(
	"""SELECT teams.date, teams.team_name, teams.opponent_name, home, 
			players.player_name, players.dk_position, players.team_name, players.afp
		FROM (SELECT date(date) as date, player_name, team_name, opponent_name, home
			FROM Playerdata			
			WHERE date(date) = '%s'
			GROUP BY 1, 2, 3) as teams
			JOIN (SELECT player_name, dk_position, team_name, avg(fp) as afp
			FROM PlayerData
			WHERE date(date) < '%s'
			GROUP BY 1, 2, 3) as players 
			ON teams.team_name = players.team_name
			AND teams.player_name = players.player_name""" % (obs_date, obs_date))
	column_names = [col[0] for col in cursor.description]
	game_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

	### Query to get current salary for player
	cursor.execute(
	""" SELECT * FROM salarydata
		WHERE date(date) = '%s'""" % (obs_date))
	column_names = [col[0] for col in cursor.description]
	salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	### Query to get fantasy points and minutes
	cursor.execute(
	""" SELECT *, date(date) as date, player_name, fp, time_to_sec(minutes) as seconds 
		FROM PlayerData 
		WHERE date(date) < '%s'
		ORDER BY date(date)
	 """ % (obs_date))
	column_names = [col[0] for col in cursor.description]
	player_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	for game in game_data:
		game_date = game['date']
		player_name = game['player_name']
		dk_position = game['dk_position']
		team_name = game['team_name']
		opponent_name = game['opponent_name']
		afp_season = float(game['afp'])
		home = game['home']
		salary = None
		for player in salary_data:
			if player_name == player['player_name']:
				salary = player['salary']
		fp_list = []
		classifier = []
		var_array = []
		minutes_list = []
		minutes_a3g = []
		minutes_list_x = []
		date_list = []
		for player in player_data:
			if player['player_name'] == player_name:
				fp = float(player['fp'])
				fp_list.append(fp)
				variables = []
				variables.append(player['home']) 
				for opponent in opponent_data:
					#if opponent['opponent_name'] == player['opponent_name'] and opponent['dk_position'] == player['dk_position']:
						#variables.append(opponent['weight'])
					if opponent['opponent_name'] == opponent_name and opponent['dk_position'] == dk_position:
						weight = opponent['weight']
				for row in plus_minus_data:
					if row['team_name'] == player['opponent_name'] and row['dk_position'] == dk_position:
						variables.append(row['plus_minus'])
					if row['team_name'] == opponent_name and row['dk_position'] == dk_position:
						plus_minus = row['plus_minus']
				date = player['date']
				date_list.append(date)
				last_game = (date-date_list[-1]).days
				if len(date_list) == 1:
					last_game = 1
				variables.append(last_game)
				afp_3g = np.average(fp_list[-3:])
				variables.append(afp_3g)

				if len(variables) == 4:
					if fp >= np.average(fp_list) + (np.std(fp_list)*.5):
						classifier.append(2)
					elif fp <=  np.average(fp_list) - (np.std(fp_list)*.5):
						classifier.append(0)
					else:
						classifier.append(1)

					minutes = float(player['seconds']) / 60
					var_array.append(variables)
					minutes_list.append(minutes)
					minutes_a3g.append([np.average(minutes_list[-3:])])
					
		
		# data = np.array(minutes_a3g)
		# target = np.array(minutes_list)
		# lin = linear_model.LinearRegression()
		# am3g = np.average(minutes_list[-3:])
		# afp_season = np.average(fp_list)
		# lin.fit(data, target)
		# pm = lin.predict([am3g])[0]
		
		# data = np.array(var_array)
		# target = np.array(fp_list)
		# lin = linear_model.LinearRegression()
		# lin.fit(data, target)
		# fppm = sum(fp_list) / sum(minutes_list)
		# pfp = pm * fppm
		
		last_game = (game_date-date_list[-1]).days
		afp_3g = np.average(fp_list[-3:])
		data = np.array(var_array)
		target = np.array(classifier)
		clf = RandomForestClassifier(n_estimators=3)
		try:
			clf.fit(data, target)
		except ValueError:
			pfp = None
			pred = None
		pm = None
		try:
			pred = clf.predict([home, plus_minus, last_game])[0]
		except ValueError:
			pfp = None
			pred = None
		# except ValueError:
		# 	pred = 3
		# 	pfp = None
		if pred == 2:
			pfp =  np.average(fp_list) + (np.std(fp_list)*.5)
		if pred == 1:
			pfp =  np.average(fp_list)
		if pred == 0:
			pfp =  np.average(fp_list) - (np.std(fp_list)*.5)

		cursor.executemany("INSERT INTO ProjectionData (date, team_name, opponent_name, player_name, dk_position, pfp, salary, afp_season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
		[(obs_date, team_name, opponent_name, player_name, dk_position, pfp, salary, afp_season)])

	
	cursor.execute("""SELECT * from ProjectionData
				WHERE salary IS NOT NULL
				ORDER BY (pfp/salary) DESC""")
	column_names = [col[0] for col in cursor.description]
	data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	team_dic = {'pg': '', 'sg': '', 'sf': '', 'pf': '', 'c': '', 'g': '', 'f': '', 'u': ''}
	players = []
	for row in data:
		player_name = row['player_name']
		position = row['dk_position'].lower()
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

	cursor.execute("""SELECT player_name, fp FROM PlayerData
					WHERE date(date) = '%s'""" % (obs_date))

	column_names = [col[0] for col in cursor.description]
	data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	actual_fp = 0
	for row in data:
		if row['player_name'] in optimal_team:
			actual_fp += row['fp']

	actual_fp_list.append(actual_fp)
	pfp_list.append(pfp)
	cursor.execute("DELETE FROM ProjectionData")
	print optimal_team, pfp, actual_fp, budget, obs_date

print np.average(actual_fp_list)
print np.std(actual_fp_list)
print max(actual_fp_list)
print actual_fp_list
print pfp_list




db.commit()
db.close()







