import requests, json, MySQLdb, itertools, scipy, math, datetime
from datetime import timedelta
from scipy import stats
from sklearn import linear_model
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
from classes import *
from functions import *
from playernames import names_dic

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()	
cursor.execute(
	"""UPDATE playerdata
		SET venue = 'h'
		WHERE home = 1""")
cursor.execute(
	"""UPDATE playerdata
		SET venue = 'a'
		WHERE home = 0""")

actual_fp_list = []
pfp_list = []
start_date = datetime.datetime(2016, 1, 15)
for x in range(0, 20):
	obs_date = str(start_date + timedelta(days=x))[:10]
	

	df = pd.read_sql("""SELECT * FROM playerdata
					WHERE date(date) < '%s' 
					ORDER BY player"""
					% (obs_date), con=db)
	home_dummies = pd.get_dummies(df.venue)
	position_dummies = pd.get_dummies(df.position)
	team_dummies = pd.get_dummies(df.opponent)
	data = pd.concat([df, home_dummies, position_dummies, team_dummies], axis=1)
	data['past_1'] = pd.rolling_mean(data.fp, 1)
	data['past_3'] = pd.rolling_mean(data.fp, 3)
	data['past_5'] = pd.rolling_mean(data.fp, 5)
	data['past_10'] = pd.rolling_mean(data.fp, 10)
	data = data[np.isfinite(data['past_1'])]
	data = data[np.isfinite(data['past_3'])]
	data = data[np.isfinite(data['past_5'])]
	data = data[np.isfinite(data['past_10'])]

	features = [
	'minutes', 'starter', 
	'C', 'PF', 'PG', 'SF', 'SG', 
	'h', 'a', 
	'atl', 'bkn', 'bos', 'cha', 'chi', 'cle',
	'dal', 'den', 'det', 'gs', 'hou', 'ind', 
	'lac', 'lal', 'mem', 'mia', 'mil', 'min', 
	'no', 'ny', 'okc', 'orl', 'phi', 'phx', 
	'por', 'sac', 'sa', 'tor', 'utah', 'wsh']

	# split data into train and test
	train, test = train_test_split(data, train_size = .8)

	x_train = train[features]
	x_test = test[features]

	y_train = train.fp
	y_test = test.fp

	### PREDICTIONS ###

	# linear regression
	model_SVR_rbf = SVR(kernel='rbf', C=.5)
	model_SVR_rbf.fit(data[features], data.fp)
	print model_SVR_rbf.score(x_test, y_test)
	

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

	# PLAYER DATA
	cursor.execute(
	""" SELECT * FROM playerdata
	WHERE date(date) < '%s'
	 ORDER BY date""" % (obs_date))
	column_names = [col[0] for col in cursor.description]
	player_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


	for row in games:
		player = row['player'].replace('.', '')
		team = row['team']
		starter = row['starter']
		position = row['position'].upper()
		venue = row['venue']
		opponent = row['opponent']
	 	minutes_list = []
	 	fp_list = []
	 	starter_list = []
	 	variables = []
	 	for next_row in player_data:
	 		if player == next_row['player'].replace('.', ''):
	 			minutes_list.append(next_row['minutes'])
	 			a3gm = np.average(minutes_list[-3:])
	 			variables.append([a3gm, next_row['starter']])
	 			fp_list.append(next_row['fp'])
		
		var_array = np.array(variables)
		target = np.array(minutes_list)
		lm = LinearRegression()
		try:
			lm.fit(var_array, target)
		except ValueError:
			pm = None
		try:	
			pm = round(lm.predict([a3gm, starter]), 2)
		except ValueError:
			pm = None

		past_1 = np.average(fp_list[-1:])
		past_3 = np.average(fp_list[-3:])
		past_5 = np.average(fp_list[-5:])
		past_10 = np.average(fp_list[-10:])			


		features[0] = pm
		features[1] = starter
		

		for row in features[2:]:
			if row == position or row == venue or row == opponent:
				features[features.index(row)] = 1
			else:
				features[features.index(row)] = 0

		if pm != None:	
			pfp = model_SVR_rbf.predict(features)[0]
	 		pfp = round(pfp, 2)

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
		if pfp >= 1 and pfp <= 150 and pm != None and pm >= 0:
			cursor.executemany("INSERT INTO ProjectionData (date, team, opponent, player, position, pfp, salary, starter, venue, pm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
			[(obs_date, team, opponent, player, position, pfp, salary, starter, venue, pm)])



	cursor.execute("""SELECT * from ProjectionData
				WHERE salary IS NOT NULL
				AND date(date) = '%s'
				ORDER BY (pfp/salary) DESC """ % (obs_date))
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
		print optimal_team, pfp, actual_fp, budget, obs_date

db.commit()
db.close()

print np.average(actual_fp_list)
print np.std(actual_fp_list)
print max(actual_fp_list)
print actual_fp_list
print pfp_list






