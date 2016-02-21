import requests, json, MySQLdb
from functions import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
cursor.execute("DELETE FROM SalaryData")

api_key = 'h5Tucd6ae2CsByRYivOL9HNqkKjtIVbg'
### Get player IDs by name
player_url = 'http://api.probasketballapi.com/player'
player_query = {'api_key': api_key}
player_data = requests.post(player_url, data=player_query).json() 

x = 1
for player in player_data:
	player_name = player['player_name']
	dk_id = player['dk_id']

	if dk_id != '':
		### Get Draft Kings Data
		dk_url = 'https://probasketballapi.com/draftkings/players'
		dk_query = {'api_key': api_key, 'player_id': dk_id}
		dk_data = requests.post(dk_url, data=dk_query).json() 
		
		for row in dk_data:
			salary = row['salary']
			date = row['updated_at']
		
			cursor.executemany("INSERT INTO SalaryData (date, player, salary) VALUES (%s, %s, %s)",
			[(date, player_name, salary)])
		
	if dk_id == '':
		print player_name

cursor.execute("DELETE FROM SalaryData WHERE date < '2015-10-01'")
db.commit()
db.close()