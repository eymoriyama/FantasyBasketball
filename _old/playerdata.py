import requests, json, MySQLdb, itertools
from difflib import SequenceMatcher
from functions import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
cursor.execute("DELETE FROM PlayerData")

### Query to get all players by position
cursor.execute("SELECT * FROM PositionData")
column_names = [col[0] for col in cursor.description]
position_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

api_key = 'JDmsH3Z0Cz5xL2KPpvTFfN9uGMtSUjnh'
### Get player IDs by name
player_url = 'http://api.probasketballapi.com/player'
player_query = {'api_key': api_key}
player_data = requests.post(player_url, data=player_query).json() 

### Get games data
game_url = 'http://api.probasketballapi.com/game'
game_query = {'api_key': api_key, 'season': 2015}
game_data = requests.post(game_url, data=game_query).json() 

### Get teams data
team_url = 'http://api.probasketballapi.com/team'
team_query = {'api_key': api_key, 'season': 2015}
team_data = requests.post(team_url, data=team_query).json() 


### Parse through every player
for player in player_data:
	player_id = updateInfo(player['id'])
	birth_date = updateInfo(player['birth_date'])	
	player_name = updateInfo(player['player_name'])
	dk_position = updateInfo(player['dk_position'])
	position = updateInfo(player['position'])
	team_id = updateInfo(player['team_id'])
	dk_player_id = updateInfo(player['dk_id'])
	
	
	### If no position give, grab position from PositionData table
	if dk_position == None:
		for row in position_data:
			if row['player_name'] == player_name:
				dk_position = row['dk_position']
	if dk_position == None:
		print player_name

	### Get updateStat(stats for each player
	stats_url = 'http://api.probasketballapi.com/boxscore/player'
	stats_query = {'api_key': api_key, 'season': 2015, 'player_id': player_id}
	stats = requests.post(stats_url, data=stats_query).json() 
	
	if dk_position == None:
		print player_name

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
		minutes = '00:' + str(minutes)

		for game in game_data:
			if game['id'] == game_id:
				home_id = game['home_id']
				away_id = game['away_id']
				date = game['date']
				if team_id == home_id:
					home = True
				if team_id == away_id:
					home = False

		for team in team_data:
			if team_id == team['id']:
				team_name = team['team_name']
				dk_team_id = team['dk_id']
				team_abbreviation = team['abbreviation']
			if opponent_id == team['id']:
				opponent_name = team['team_name']
				opponent_abbreviation = team['abbreviation']


			
		cursor.executemany("INSERT INTO PlayerData (date, player_name, dk_player_id, position, dk_position, birth_date, dk_team_id, period, fp, points, minutes, fta, ftm, fouls, blocks, fga, fgm, fg3a, fg3m, rebounds, steals, assists, turnovers, plus_minus, home, team_name, opponent_name, opponent_abbreviation, team_abbreviation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
		[(date, player_name, dk_player_id, position, dk_position, birth_date, dk_team_id, period, fp, points, minutes, fta, ftm, fouls, blocks, fga, fgm, fg3a, fg3m, rebounds, steals, assists, turnovers, plus_minus, home, team_name, opponent_name, opponent_abbreviation, team_abbreviation)])



db.commit()
db.close()

	
