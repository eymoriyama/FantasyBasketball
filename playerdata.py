import MySQLdb, itertools, requests, json
from datetime import timedelta
from datetime import datetime, date
from bs4 import BeautifulSoup
import pandas as pd
from functions import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

window = 10
today = datetime.now()
start_date =str(today - timedelta(days=window))[:10]
cursor.execute("DELETE FROM playerdata >= '%s'" % (start_date))
cursor.execute("""SELECT * 
				FROM games 
				WHERE match_id IS NOT NULL
				AND date(date) >= '%s'
				GROUP BY match_id""" % (start_date))
column_names = [col[0] for col in cursor.description]
games = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


base_url = 'http://espn.go.com/nba/boxscore?id='
for game in games:
	match_id = game['match_id']
	date = game['date']
	home_team = game['home_team']
	away_team = game['away_team']
	url = base_url + str(match_id)
	request = requests.get(url)
	soup = BeautifulSoup(request.text, 'lxml')
	table = soup.find(class_='row-wrapper')
	try:
		bodies = table.find_all('tbody')
		away_team_starters = bodies[0].find_all('tr')
		home_team_starters = bodies[2].find_all('tr')
		starters_stats = getPlayerStats(away_team_starters, away_team, home_team, 0, 1) + getPlayerStats(home_team_starters, home_team, away_team, 1, 1)
		away_team_bench = bodies[1].find_all('tr')[:-2]
		home_team_bench = bodies[3].find_all('tr')[:-2]
		bench_stats = getPlayerStats(away_team_bench, away_team, home_team, 0, 0) + getPlayerStats(home_team_bench, home_team, away_team, 1, 0)
		stats_array = starters_stats + bench_stats
	except AttributeError:
		print game
		stats_array = []
	
	for stat in stats_array:
		player = stat['player']
		player_id = stat['player_id']
		position = stat['position']
		home = stat['home']
		starter = stat['starter']
		team = stat['team']
		opponent = stat['opponent']
		minutes = stat['minutes']
		fgm = stat['fgm']
		fga = stat['fga']
		fg3a = stat['fg3a']
		fg3m = stat['fg3m']
		fta = stat['fta']
		ftm = stat['ftm']
		oreb = stat['oreb']
		dreb = stat['dreb']
		rebounds = stat['rebounds']
		assists = stat['assists']
		steals = stat['steals']
		blocks = stat['blocks']
		turnovers = stat['turnovers']
		fouls = stat['fouls']
		plus_minus = stat['plus_minus']
		points = stat['points']
		fp = stat['fp']
		note = stat['note']
		played = stat['played']

		cursor.executemany("INSERT INTO playerdata (date, match_id, player, player_id, position, team, opponent, fp, points, minutes, fta, ftm, fouls, blocks, fga, fgm, fg3a, fg3m, oreb, dreb, rebounds, steals, assists, turnovers, plus_minus, home, starter, played, note) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
		[(date, match_id, player, player_id, position, team, opponent, fp, points, minutes, fta, ftm, fouls, blocks, fga, fgm, fg3a, fg3m, oreb, dreb, rebounds, steals, assists, turnovers, plus_minus, home, starter, played, note)])


db.commit()
db.close()



