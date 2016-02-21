import requests, json, MySQLdb, itertools, scipy, math, datetime
from datetime import timedelta
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from fuzzywuzzy import fuzz
import numpy as np
from classes import *
from functions import *
from playernames import names_dic

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()
cursor.execute("DELETE FROM projectiondata")


outliers = []
actual_fp_list = []
pfp_list = []
start_date = datetime.datetime(2016, 1, 1)
for x in range(0, 38):
	obs_date = str(start_date + timedelta(days=x))[:10]

	# PLUS MINUS DATA
	cursor.execute(
	"""	SELECT team, second_position, avg(plus_minus) as plus_minus
		FROM playerdata 
		WHERE date(date) < '%s'
		AND starter = 1
		GROUP BY 1, 2 """ % (obs_date))
	column_names = [col[0] for col in cursor.description]
	plus_minus_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	
	# PLAYERS WHO PLAYED ON OBSERVATION DATE
	cursor.execute(
	"""SELECT date(date) as date, player, position, second_position, 
			team, opponent, home, starter
			FROM Playerdata			
			WHERE date(date) = '%s'
			AND played = 1 """ % (obs_date))
	column_names = [col[0] for col in cursor.description]
	game_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

	
	# SALARY DATA
	cursor.execute(
	""" SELECT * FROM salarydata
		WHERE date(date) = '%s'""" % (obs_date))
	column_names = [col[0] for col in cursor.description]
	salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	### PLAYER STATS
	cursor.execute(
	""" SELECT *, date(date) as date
		FROM PlayerData 
		WHERE date(date) < '%s'
		ORDER BY date(date)
	 """ % (obs_date))
	column_names = [col[0] for col in cursor.description]
	player_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

	output = []
	for game in game_data:
		game_date = game['date']
		player = game['player'].replace('.', '')
		position = game['position']
		second_position = game['second_position']
		team = game['team']
		opponent = game['opponent']
		home = game['home']
		starter = game['starter']
		
		# GRAB PLAYER SALARY
		salary = None
		for row in salary_data:
			player_name = row['player'].replace('.', '')
			try:
				player_name = names_dic[player_name]
			except KeyError:
				pass
			if player == player_name:
				salary = row['salary']
	
		
		minutes_list = []
		fp_list = []
		predictor = []
		var_array = []
		date_list = []
		for row in player_data:
			if player == row['player'].replace('.', ''):
				fp = float(row['fp'])
				fp_list.append(fp)
				minutes = float(row['minutes'])
				minutes_list.append(minutes)
				
				
				# Y - MINUTES PLAYED
				predictor.append(minutes)
				
				variables = []
				# X1 - STARTED 
				variables.append(row['starter'])
				
				# X3 - LAST 3 GAMES AVERAGE MINUTES
				amp3g = np.average(minutes_list[-3:])
				variables.append(amp3g)
		
				var_array.append(variables)
	
		amp3g = np.average(minutes_list[-3:])
		try:
			fppm = sum(fp_list) / sum(minutes_list)
		except ZeroDivisionError:
			fppm = 0
		data = np.array(var_array)
		target = np.array(predictor)
		clf = RandomForestClassifier(n_estimators=2)
		
		try:
			clf.fit(data, target)
		except ValueError:
			pm = None
		
		prediction = np.array([[starter, amp3g]])
		try:
			pm = clf.predict(prediction)
		except ValueError:
			pm = None
			
		if pm == None:
			pfp = 0

		if pm != None:
			pfp = round(pm * fppm, 2)
		

		
		cursor.executemany("INSERT INTO ProjectionData (date, team, opponent, player, position, pfp, salary, starter, home) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
		[(obs_date, team, opponent, player, position, pfp, salary, starter, home)])

		
	cursor.execute("""SELECT * from ProjectionData
				WHERE salary IS NOT NULL
				AND starter = 1
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
		player = Player(position, p`layer_name, salary, pfp, value)
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





