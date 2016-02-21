import requests, json, MySQLdb, itertools, scipy, math
from functions import *
from scipy import stats
import numpy as np

db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()
cursor.execute("DELETE FROM ProjectionData")
### Query to get points allowed per position
cursor.execute(
"""SELECT teams.opponent_name, players.dk_position, 
		sum(teams.act_fp), sum(players.exp_fp),
		 sum(teams.act_fp)/sum(players.exp_fp) as weight
	FROM (SELECT date, team_name, opponent_name, player_name, dk_position, sum(fp) as act_fp
			FROM PlayerData
			WHERE dk_position IS NOT NULL
			GROUP BY 1, 2, 3, 4, 5) as teams
	LEFT JOIN (SELECT player_name, dk_position, avg(fp) as exp_fp
				FROM PlayerData
				WHERE dk_position IS NOT NULL
				GROUP BY 1) as players
				ON teams.dk_position = players.dk_position AND teams.player_name = players.player_name
				GROUP BY 1, 2 """)
column_names = [col[0] for col in cursor.description]
opponent_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

obs_date = '2016-02-10'
cursor.execute(
"""SELECT teams.date, teams.home_team, teams.away_team, 
		players.player_name, players.dk_position, players.team_name, players.afp,
		CASE WHEN players.team_name = teams.home_team THEN teams.away_team
		WHEN players.team_name = teams.away_team THEN teams.home_team
		END AS opponent_name
	FROM  (SELECT date, home_team, away_team
		FROM GameData
		WHERE date(date) = '%s') as teams
		JOIN (SELECT player_name, dk_position, team_name, avg(fp) as afp
		FROM PlayerData
		WHERE date(date) <=  '%s'
		GROUP BY 1, 2, 3) as players 
		ON teams.home_team = players.team_name or teams.away_team = players.team_name""" % (obs_date, obs_date))
column_names = [col[0] for col in cursor.description]
game_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]

### Query to get current salary for player
cursor.execute(
""" SELECT * FROM
	(SELECT date, player_name, salary
	FROM SalaryData) as a
	JOIN (SELECT player_name, max(date) as max_date
	FROM SalaryData group by 1) as b
	ON a.date = b.max_date and a.player_name = b.player_name
 """)
column_names = [col[0] for col in cursor.description]
salary_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


### Query to get fantasy points and minutes
cursor.execute(
""" SELECT *, date(date), player_name, fp, time_to_sec(minutes) as seconds 
	FROM PlayerData 
	ORDER BY date(date)
 """)
column_names = [col[0] for col in cursor.description]
player_data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]


for game in game_data:
	date = game['date']
	player_name = game['player_name']
	dk_position = game['dk_position']
	team_name = game['team_name']
	opponent_name = game['opponent_name']
	afp_season = float(game['afp'])
	if team_name == game['home_team']:
		home = True 
	else:
		home = False


	### Get opponent defensive weight
	for opponent in opponent_data:
		if opponent_name == opponent['opponent_name'] and dk_position == opponent['dk_position']:
			weight = float(opponent['weight'])

	### Get list of fantasy points per game
	fp_home_list, fp_away_list = [], []
	fgp_home_list, fgp_away_list = [], []
	fp_list, points_list, assists_list, rebounds_list, blocks_list, steals_list, fg3m_list, to_list, minutes_list = [], [], [], [], [], [], [], [], []
	for player in player_data:
		if player_name == player['player_name']:
			fp_list.append(player['fp'])
			points_list.append(player['points'])
			assists_list.append(player['assists'])
			rebounds_list.append(player['rebounds'])
			blocks_list.append(player['blocks'])
			steals_list.append(player['steals'])
			fg3m_list.append(player['fg3m'])
			to_list.append(player['turnovers'])
			minutes = float(player['seconds']) / 60
			minutes_list.append(minutes)
			if player['home'] == 1:
				fp_home_list.append(player['fp'])
				try:
					fgp_home_list.append(float(player['fgm'])/float(player['fga']))
				except ZeroDivisionError:
					pass
			if player['home'] == 0:
				fp_away_list.append(player['fp'])
				try:
					fgp_away_list.append(float(player['fgm'])/float(player['fga']))
				except ZeroDivisionError:
					pass

	fp_list_5g = fp_list[-5:]
	afp_5g = np.average(fp_list_5g)
	fp_list_season = fp_list[:-5]
	pvalue_5g = scipy.stats.ttest_ind(fp_list_season, fp_list_5g, axis=None, equal_var=False)[1]

	fp_list_10g = fp_list[-10:]
	afp_10g = np.average(fp_list_10g)
	fp_list_season = fp_list[:-10]
	pvalue_10g = scipy.stats.ttest_ind(fp_list_season, fp_list_10g, axis=None, equal_var=False)[1]
	pfp = afp_season * weight

	trend = None
	if pvalue_5g <= .05:
		pfp = afp_5g * weight
	if pvalue_5g <= .1:	
		if afp_5g > afp_season:
			trend = 'positive'
		if afp_5g < afp_season:
			trend = 'negative'
		obs_window = 5
	

	if pvalue_10g <= .05 and pvalue_10g < pvalue_5g:
		if afp_10g > afp_season:
			trend = 'positive'
		if afp_10g < afp_season:
			trend = 'negative'
		pfp = afp_10g * weight
		obs_window = 10
		
	
	if pvalue_5g > .05 and pvalue_10g > .05:
		pfp = afp_season * weight
		obs_window = len(fp_list)

	std = np.std(fp_list)
	var = np.var(fp_list)
	ceiling = afp_season + (std)
	ampg = np.average(minutes_list)
	var_min = np.std(minutes_list)

	points_floor = np.average(points_list) - np.std(points_list)
	assists_floor = np.average(assists_list) - np.std(assists_list)
	rebounds_floor = np.average(rebounds_list) - np.std(rebounds_list)
	blocks_floor = np.average(blocks_list) - np.std(blocks_list)
	steals_floor = np.average(steals_list) - np.std(steals_list)
	fg3m_floor = np.average(fg3m_list) - np.std(fg3m_list)
	to_ceiling = np.average(to_list) + np.std(to_list)
	
	points_ceiling = np.average(points_list) + np.std(points_list)
	assists_ceiling = np.average(assists_list) + np.std(assists_list)
	rebounds_ceiling = np.average(rebounds_list) + np.std(rebounds_list)
	blocks_ceiling = np.average(blocks_list) + np.std(blocks_list)
	steals_ceiling = np.average(steals_list) + np.std(steals_list)
	fg3m_ceiling = np.average(fg3m_list) + np.std(fg3m_list)
	to_floor = np.average(to_list) - np.std(to_list)


	for stat in [points_floor, assists_floor, rebounds_floor, blocks_floor, steals_floor, fg3m_floor, to_floor]:
		if stat < 0:
			stat = 0.0

	floor = calculateFantasyPoints(points_floor, fg3m_floor, rebounds_floor, assists_floor, steals_floor, blocks_floor, to_ceiling)
	ceiling = calculateFantasyPoints(points_ceiling, fg3m_ceiling, rebounds_ceiling, assists_ceiling, steals_ceiling, blocks_ceiling, to_ceiling)


	pvalue_home = scipy.stats.ttest_ind(fp_home_list, fp_away_list, axis=None, equal_var=False)[1]
	home_away = None
	if pvalue_home < .05:
		if home == True:
			pfp = np.average(fp_home_list) * weight
			floor = np.average(fp_home_list) - np.std(fp_home_list)
			ceiling = np.average(fp_home_list) + np.std(fp_home_list)
		if home == False:	
			pfp = np.average(fp_away_list) * weight
			floor = np.average(fp_away_list) - np.std(fp_home_list)
			ceiling = np.average(fp_away_list) + np.std(fp_away_list)
		if np.average(fp_home_list) > np.average(fp_away_list):
			home_away = 'home'
		if np.average(fp_home_list) < np.average(fp_away_list):
			home_away = 'away'
	home_avg = np.average(fp_home_list)
	away_avg = np.average(fp_away_list)

	floor = round(floor, 1)

	### Get salary data	
	salary = None
	for player in salary_data:
		if player_name == player['player_name']:
			salary = player['salary']
	for stat in [pvalue_5g, pvalue_10g, pvalue_home]:
		if math.isnan(stat):
			stat = 0
			obs_window = len(fp_list)
		if stat < 0:
			stat = 0

	if math.isnan(pvalue_5g):
		pvalue_5g = 0
	if math.isnan(pvalue_10g):
		pvalue_10g = 0
	if math.isnan(pvalue_home):
		pvalue_home = 0
	if math.isnan(home_avg):
		home_avg = 0
	if math.isnan(away_avg):
		away_avg = 0


	cursor.executemany("INSERT INTO ProjectionData (date, team_name, opponent_name, player_name, dk_position, afp_season, afp_5g, afp_10g, pfp, weight, obs_window, trend, pvalue_5g, pvalue_10g, salary, std, var, floor, ceiling, var_min, ampg, pvalue_home, home_avg, away_avg, home_away, home) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
	[(date, team_name, opponent_name, player_name, dk_position, afp_season, afp_5g, afp_10g, pfp, weight, obs_window, trend, pvalue_5g, pvalue_10g, salary, std, var, floor, ceiling, var_min, ampg, pvalue_home, home_avg, away_avg, home_away, home)])

db.commit()
db.close()





