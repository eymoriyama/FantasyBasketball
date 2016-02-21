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
from playernames import *
from city_dic import *


# UPDATES TO TABLE
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


# DUMMY VARIABLES
df = pd.read_sql("""SELECT * FROM playerdata ORDER BY player""", con=db)
home_dummies = pd.get_dummies(df.venue)
position_dummies = pd.get_dummies(df.position)
team_dummies = pd.get_dummies(df.opponent)
data = pd.concat([df, home_dummies, position_dummies, team_dummies], axis=1)

### X AND Y
features = ['minutes', 'C', 
'PF', 'PG', 'SF', 'SG', 'h', 'a',
'atl', 'bkn',
'bos', 'cha', 'chi', 'cle', 'dal',
'den', 'det', 'gs', 'hou', 'ind', 'lac', 
'lal', 'mem', 'mia', 'mil', 'min', 'no', 
'ny', 'okc', 'orl', 'phi', 'phx', 'por',
'sac', 'sa', 'tor', 'utah', 'wsh']
x = data[features]
y = data.fp

### PREDICTIONS ###
lm = LinearRegression()
lm.fit(x, y)
coefs = zip(features, lm.coef_)
print coefs
coefs_dic = {}
for row in coefs:
	coefs_dic[row[0]] = row[1]
print coefs_dic


# GAMES FOR A GIVEN NIGHT
date = '2016-02-20'
cursor.execute("DELETE FROM projectiondata")
cursor.execute(
	"""SELECT *, players.team,
	CASE WHEN players.team = games.home_team THEN 'h'
	WHEN players.team = games.away_team THEN 'a'
	END venue,
	CASE WHEN players.team = games.home_team THEN games.away_team	
	WHEN players.team = games.away_team THEN games.home_team
	END opponent
	FROM (SELECT * 
		FROM games 
		WHERE date(date) = '%s') as games
		JOIN 
		(SELECT player, team, starter, position
		FROM depthcharts) AS players
		ON players.team = games.home_team OR players.team = games.away_team""" % (date))
column_names = [col[0] for col in cursor.description]
games = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


# SALARY DATA
cursor.execute(
""" SELECT * FROM
	(SELECT date, player, salary
	FROM SalaryData) as a
	JOIN (SELECT player, max(date) as max_date
	FROM SalaryData group by 1) as b
	ON a.date = b.max_date and a.player = b.player
 """)
column_names = [col[0] for col in cursor.description]
salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


# PLAYER DATA
cursor.execute(
""" SELECT * FROM playerdata ORDER BY date""")
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
 	starter_list = []
 	variables = []
 	for next_row in player_data:
 		if player == next_row['player'].replace('.', ''):
 			minutes_list.append(next_row['minutes'])
 			a3gm = np.average(minutes_list[-3:])
 			variables.append([a3gm, next_row['starter']])
	
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
	if pm != None:
		pfp = (pm * coefs_dic['minutes']) + coefs_dic[position] + coefs_dic[venue] + coefs_dic[opponent]
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

	print pfp, pm
	if pfp >= 0 and pm != None and pm >= 0:
		cursor.executemany("INSERT INTO ProjectionData (date, team, opponent, player, position, pfp, salary, starter, venue, pm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
		[(date, team, opponent, player, position, pfp, salary, starter, venue, pm)])

db.commit()
db.close()
