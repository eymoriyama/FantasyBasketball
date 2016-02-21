import requests, json, MySQLdb
from functions import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()

### Get games data
game_url = 'http://api.probasketballapi.com/game'
game_query = {'api_key': '726CezU3qrjxVnLXWBhOcPvoyw0Atuf4', 'season': 2015}
game_data = requests.post(game_url, data=game_query).json() 

### Get teams data
teams_url = 'http://api.probasketballapi.com/team'
teams_query = {'api_key': '726CezU3qrjxVnLXWBhOcPvoyw0Atuf4', 'season': 2015}
teams_data = requests.post(teams_url, data=teams_query).json() 

for game in game_data:
	date = game['date']
	home_id = game['home_id']
	away_id = game['away_id']
	game_id = game['id']

	for team in teams_data:
		if home_id == team['id']:
			home_team = team['team_name']
			home_abbreviation = team['abbreviation']
		if away_id == team['id']:
			away_team = team['team_name']
			away_abbreviation = team['abbreviation']

	cursor.executemany("INSERT INTO GameData (date, home_team, away_team, home_abbreviation, away_abbreviation, game_id) VALUES (%s, %s, %s, %s, %s, %s)",
	[(date, home_team, away_team, home_abbreviation, away_abbreviation, game_id)])

db.commit()
db.close()

