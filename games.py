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

cursor.execute("SELECT * from teams")
column_names = [col[0] for col in cursor.description]
teams = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

base_url =  'http://espn.go.com/nba/team/schedule/_/name/'
year = '2016'
x = 0
games = []
future_games = []
while True:
	team = teams[x]['team']
	url = base_url + teams[x]['team'] + '/' + year + '/' + teams[x]['prefix']
	r = requests.get(url)
	table = BeautifulSoup(r.text).table
	for row in table.find_all('tr')[1:]:
		columns = row.find_all('td')
		try:
			games_dic = {}
			match_id = columns[2].a['href'].split('?id=')[1]
			games_dic['match_id'] = match_id
		except Exception:
			match_id = None
		try:
			games_dic = {}
			_home = True if columns[1].li.text == 'vs' else False
			d = datetime.strptime(columns[0].text, '%a, %b %d')
			logo_link = columns[1].img['src']
			opp = (logo_link.split('/')[-1]).split('.')[0]
			if d.month >= 10:
				game_date = date(int(year)-1, d.month, d.day)
			if d.month < 10:
				game_date = date(int(year), d.month, d.day)
			if _home:
				home_team = team
				away_team = opp.lower()
			if _home == False:
				home_team = opp.lower()
				away_team = team
  			games_dic['date'] = game_date
  			games_dic['home_team'] = home_team
  			games_dic['away_team'] = away_team
  			games_dic['match_id'] = match_id
  			games.append(games_dic)
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
	if (date, home_team, away_team) not in output:
		cursor.executemany("INSERT INTO games (date, match_id, home_team, away_team) VALUES (%s, %s, %s, %s)", 
		[(date, match_id, home_team, away_team)])
		output.append((date, home_team, away_team))


db.commit()
db.close()

