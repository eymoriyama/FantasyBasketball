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
cursor.execute("DELETE FROM depthcharts")
cursor.execute(
	"""SELECT * FROM teams""")
column_names = [col[0] for col in cursor.description]
teams = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

base_url = 'http://espn.go.com/nba/team/depth/_/name/'
for row in teams:
	players = []
	team_full_name = row['team_full_name']
	team = row['team']
	prefix = row['prefix']
	url = base_url + team + '/' + prefix
	request = requests.get(url)
	soup = BeautifulSoup(request.text)
	for odd_even in ['oddrow', 'evenrow']:
		position_row = soup.find_all('tr', class_=odd_even)
		for row in position_row:
			col = row.find_all('td')
			for next_row in col:
				if next_row.contents[0] == 'Point Guard':
					position = 'pg'
				if next_row.contents[0] == 'Small Forward':
					position = 'sf'
				if next_row.contents[0] == 'Shooting Guard':
					position = 'sg'
				if next_row.contents[0] == 'Power Forward':
					position = 'pf'
				if next_row.contents[0] == 'Center':
					position = 'c'
				try:
					player_dic = {}
					player_dic['starter'] = 1
					player_dic['player'] = next_row.a.b.contents[0]
					player_dic['player_id'] = next_row.a['href'].split('/')[-2]
					player_dic['position'] = position
					players.append(player_dic)
				except AttributeError:
					try:
						player_dic = {}
						player_dic['starter'] = 0
						player_dic['player'] = next_row.a.contents[0]
						player_dic['player_id'] = next_row.a['href'].split('/')[-2]
						player_dic['position'] = position
						players.append(player_dic)
					except AttributeError:
						pass
	for player in players:
		cursor.executemany("INSERT INTO depthcharts (team_full_name, team, prefix, player, player_id, position, starter) VALUES (%s, %s, %s, %s, %s, %s, %s)",
		[(team_full_name, team, prefix, player['player'], player['player_id'], player['position'], player['starter'])])


db.commit()
db.close()


				
