import MySQLdb, itertools, requests, json
from datetime import datetime, date
from bs4 import BeautifulSoup
import pandas as pd

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
cursor.execute("DELETE FROM games")

cursor.execute("SELECT * from teams LIMIT 10")
column_names = [col[0] for col in cursor.description]
teams = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

base_url =  'http://espn.go.com/nba/team/schedule/_/name/'
year = '2016'
x = 0
games = []
future_games = []
while True:
	team = teams[x]['team']
	url = base_url + teams[x]['city'] + '/' + year + '/' + teams[x]['prefix']
	print url
	r = requests.get(url)
	table = BeautifulSoup(r.text).table
	for row in table.find_all('tr')[1:]:
		columns = row.find_all('td')
		try:
			games_dic = {}
			_home = True if columns[1].li.text == 'vs' else False
			match_id = columns[2].a['href'].split('?id=')[1]
			score = columns[2].a.text.split(' ')[0].split('-')
			score = [int(i) for i in score]
			won = columns[2].span.text
			d = datetime.strptime(columns[0].text, '%a, %b %d')
			if d.month >= 10:
				game_date = date(int(year)-1, d.month, d.day)
			if d.month < 10:
				game_date = date(int(year), d.month, d.day)
			if _home:
				home_team = team
				away_team = columns[1].find_all('a')[1].text
			if _home == False:
				home_team = columns[1].find_all('a')[1].text
				away_team = team
  			games_dic['match_id'] = match_id
  			games_dic['date'] = game_date
  			games_dic['home_team'] = home_team
  			games_dic['away_team'] = away_team
  			games_dic['score'] = score
  			games_dic['won'] = won
  			games.append(games_dic)
  			print game_date, home_team, away_team
		except Exception:
			try:
				games_dic = {}
				_home = True if columns[1].li.text == 'vs' else False
				d = datetime.strptime(columns[0].text, '%a, %b %d')
				if d.month >= 10:
					game_date = date(int(year)-1, d.month, d.day)
				if d.month < 10:
					game_date = date(int(year), d.month, d.day)
				if _home:
					home_team = team
					away_team = columns[1].find_all('a')[1].text
				if _home == False:
					home_team = columns[1].find_all('a')[1].text
					away_team = team
	  			games_dic['match_id'] = None
	  			games_dic['date'] = game_date
	  			games_dic['home_team'] = home_team
	  			games_dic['away_team'] = away_team
	  			games_dic['score'] = None
	  			games_dic['won'] = None
	  			future_games.append(games_dic)
			except Exception:
				pass
	x += 1
	if x == 30:
		break

output = []
for row in games:
	match_id = row['match_id']
	date = row['date']
	home_team = row['home_team']
	away_team = row['away_team']
	for next_row in games:
		if next_row['match_id'] == match_id and next_row['home_team'] != row['home_team']:
			if len(next_row['home_team']) > len(row['home_team']):
				home_team = next_row['home_team']
				away_team = row['away_team']
				if next_row['won'] == 'W':
					home_team_score = max(next_row['score'])
					away_team_score = min(next_row['score'])
				else:
					home_team_score = min(next_row['score'])
					away_team_score = max(next_row['score'])
			if len(next_row['home_team']) < len(row['home_team']):
				home_team = row['home_team']
				away_team = next_row['away_team']
				if row['won'] == 'W':
					home_team_score = max(row['score'])
					away_team_score = min(row['score'])
				else:
					home_team_score = min(next_row['score'])
					away_team_score = max(next_row['score'])
			if (match_id) not in output:
				cursor.executemany("INSERT INTO games (date, match_id, home_team, away_team, home_team_score, away_team_score) VALUES (%s, %s, %s, %s, %s, %s)", 
				[(date, match_id, home_team, away_team, home_team_score, away_team_score)])
				output.append(match_id)
output = []
for row in future_games:
	match_id = row['match_id']
	date = row['date']
	home_team = row['home_team']
	away_team = row['away_team']
	home_team_score = None
	away_team_score = None
	cursor.executemany("INSERT INTO games (date, match_id, home_team, away_team, home_team_score, away_team_score) VALUES (%s, %s, %s, %s, %s, %s)", 
	[(date, match_id, home_team, away_team, home_team_score, away_team_score)])

db.commit()
db.close()

