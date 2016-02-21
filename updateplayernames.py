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
cursor.execute("SELECT distinct(player_id), player FROM playerdata")
column_names = [col[0] for col in cursor.description]
players = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

# base_url = 'http://espn.go.com/nba/player/_/id/'
# for row in players:
# 	player_id = row['player_id']
# 	short_name = row['player']
# 	url = base_url + str(player_id)
# 	request = requests.get(url)
# 	soup = BeautifulSoup(request.text, 'lxml')
# 	try:
# 		player = soup.find(class_='main-headshot').img['alt']
# 		cursor.executemany("INSERT INTO playernames (player_id, short_name, player) VALUES (%s, %s, %s)",
# 		[(player_id, short_name, player)])
# 	except AttributeError:
# 		print row
# 		pass
	
cursor.execute(
"""UPDATE playerdata
	LEFT JOIN playernames
	ON playerdata.player_id = playernames.player_id 
	SET playerdata.player = playernames.player
	WHERE playernames.player IS NOT NULL""")

db.commit()
db.close()
	


