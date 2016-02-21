import requests, json, MySQLdb, itertools, scipy, math
from functions import *
from scipy import stats
from sklearn import linear_model
import numpy as np

db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()
cursor.execute("DELETE FROM ProjectionData")
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


cursor.execute(
"""	SELECT team_name, dk_position, avg(plus_minus) as plus_minus
 	FROM playerdata 
 	GROUP BY 1, 2 """)
column_names = [col[0] for col in cursor.description]
plus_minus_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


obs_date = '2016-02-09'
cursor.execute(
"""SELECT teams.date, teams.home_team, teams.away_team, teams.home,
		players.player_name, players.dk_position, players.team_name, players.afp,
		CASE WHEN players.team_name = teams.home_team THEN teams.away_team
		WHEN players.team_name = teams.away_team THEN teams.home_team
		END AS opponent_name
	FROM  (SELECT date, home_team, away_team
		FROM GameData
		WHERE date(date) = '%s') as teams
		JOIN (SELECT player_name, dk_position, team_name, avg(fp) as afp
		FROM PlayerData
		WHERE date(date) <=  '%s'
		GROUP BY 1, 2, 3) as players 
		ON teams.home_team = players.team_name or teams.away_team = players.team_name
		WHERE players.afp > 10""" % (obs_date, obs_date))
column_names = [col[0] for col in cursor.description]
game_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

### Query to get current salary for player
cursor.execute(
""" SELECT * FROM
	(SELECT date, player_name, salary
	FROM SalaryData) as a
	JOIN (SELECT player_name, max(date) as max_date
	FROM SalaryData group by 1) as b
	ON a.date = b.max_date and a.player_name = b.player_name
 """)
column_names = [col[0] for col in cursor.description]
salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


### Query to get fantasy points and minutes
cursor.execute(
""" SELECT *, date(date), player_name, fp, time_to_sec(minutes) as seconds 
	FROM PlayerData 
	ORDER BY date(date)
 """)
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
	
	last_game = (game_date-date_list[-1]).days
	afp_3g = np.average(fp_list[-3:])
	data = np.array(var_array)
	target = np.array(classifier)
	clf = RandomForestClassifier(n_estimators=4)
	afp_season = np.average(fp_list)
	try:
		clf.fit(data, target)
	except ValueError:
		pfp = None
		pred = None
	
	try:
		pred = clf.predict([home, plus_minus, last_game, afp_3g])[0]
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

	
	
	cursor.executemany("INSERT INTO ProjectionData (date, team_name, opponent_name, player_name, dk_position, pfp, salary, afp_season, pred) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
	[(date, team_name, opponent_name, player_name, dk_position, pfp, salary, afp_season, pred)])

db.commit()
db.close()





