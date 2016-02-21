import requests, json, MySQLdb
from functions import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

### Get player IDs bye
players_url = 'http://api.probasketballapi.com/player'
players_query = {'api_key': '726CezU3qrjxVnLXWBhOcPvoyw0Atuf4'}
players_data = requests.post(players_url, data=players_query).json() 


### Get games data
games_url = 'http://api.probasketballapi.com/game'
games_query = {'api_key': '726CezU3qrjxVnLXWBhOcPvoyw0Atuf4', 'season': 2015}
games_data = requests.post(games_url, data=games_query).json() 

### Get teams data
teams_url = 'http://api.probasketballapi.com/team'
teams_query = {'api_key': '726CezU3qrjxVnLXWBhOcPvoyw0Atuf4', 'season': 2015}
teams_data = requests.post(teams_url, data=teams_query).json() 


### Parse through every player
for player in players_data:
	player_id = updateInfo(player['id'])
	birth_date = updateInfo(player['birth_date'])	
	player_name = updateInfo(player['player_name'])
	dk_position = updateInfo(player['dk_position'])
	position = updateInfo(player['position'])
	team_id = updateInfo(player['team_id'])
	dk_player_id = updateInfo(player['dk_id'])
	
	### Get updateStat(stats for each player
	stats_url = 'http://api.probasketballapi.com/boxscore/player'
	stats_query = {'api_key': '726CezU3qrjxVnLXWBhOcPvoyw0Atuf4', 'season': 2015, 'player_id': player_id}
	stats = requests.post(stats_url, data=stats_query).json() 
	

	for stat in stats:
		period = updateStat(stat['period'])
		team_id = updateStat(stat['team_id'])
		points = updateStat(stat['pts'])
		minutes = updateMinutes(updateStat(stat['min']))
		fta = updateStat(stat['fta'])
		ftm = updateStat(stat['ftm'])
		turnovers = updateStat(stat['to'])
		fouls = updateStat(stat['pf'])
		blocks = updateStat(stat['blk'])
		fga = updateStat(stat['fga'])
		fgm = updateStat(stat['fgm'])
		fg3a = updateStat(stat['fg3a'])
		fg3m = updateStat(stat['fg3m'])
		assists = updateStat(stat['ast'])
		oreb = updateStat(stat['oreb'])
		dreb = updateStat(stat['dreb'])
		rebounds = oreb + dreb
		steals = updateStat(stat['stl'])
		plus_minus = updateStat(stat['plus_minus'])
		opponent_id = updateStat(stat['opponent_id'])
		game_id = updateStat(stat['game_id'])
		fp = calculateFantasyPoints(points, fg3m, rebounds, assists, steals, blocks, turnovers)

		for game in games_data:
			if game['id'] == game_id:
				home_id = game['home_id']
				away_id = game['away_id']
				date = game['date']
				if team_id == home_id:
					home = True
				if team_id == away_id:
					home = False

		for team in teams_data:
			if team_id == team['id']:
				team_name = team['team_name']
				dk_team_id = team['dk_id']
				team_abbreviation = team['abbreviation']
			if opponent_id == team['id']:
				opponent_name = team['team_name']
				opponent_abbreviation = team['abbreviation']




		cursor.executemany("INSERT INTO PlayerStats (date, player_name, dk_player_id, position, dk_position, birth_date, dk_team_id, period, fp, points, minutes, fta, ftm, fouls, blocks, fga, fgm, fg3a, fg3m, rebounds, steals, assists, turnovers, plus_minus, home, team_name, opponent_name, opponent_abbreviation, team_abbreviation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
		[(date, player_name, dk_player_id, position, dk_position, birth_date, dk_team_id, period, fp, points, minutes, fta, ftm, fouls, blocks, fga, fgm, fg3a, fg3m, rebounds, steals, assists, turnovers, plus_minus, home, team_name, opponent_name, opponent_abbreviation, team_abbreviation)])



db.commit()
db.close()


	
