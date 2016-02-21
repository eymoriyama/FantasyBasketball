from classes import *

def optimizeTeam(team, players):
	if team.budget <= 50000:
		team.players_list.sort(key=lambda x: x.pfp)
		players.sort(key=lambda x: x.pfp, reverse=True)
		for player in team.players_list:
			for position in team.positions:
				if team.team_dic[position] == player:
					position_out = position
			for sub in players:
				if sub not in team.players_list and (sub.position == position_out or sub.second_position == position_out or sub.third_position == position_out):
					if sub.pfp > player.pfp and sub.salary <= (50000-team.budget) + player.salary:
						out = team.team_dic[position_out]
						team.team_dic[position_out] = sub
						team = Team(team.team_dic)
						if not team.under_budget:
							team.team_dic[position_out] = out
							team = Team(team.team_dic)
						break
		return team.players, team.budget, team.points
	else:
		team.players_list.sort(key=lambda x: x.salary, reverse=True)
		players.sort(key=lambda x: x.pfp, reverse=True)
		for player in team.players_list:
			for position in team.positions:
				if team.team_dic[position] == player:
					position_out = position
			for sub in players:
				if sub not in team.players_list and (sub.position == position_out or sub.second_position == position_out or sub.third_position == position_out):
					team.team_dic[position_out] = sub
					team = Team(team.team_dic)
					if team.under_budget:
						return team.players, team.budget, team.points
		return team.players, team.budget, team.points


def getPlayerStats(players, team, opponent, home, starter):
	stats_array = []
	for row in players:
		try:
			stats_dic = {}
			cols = row.find_all('td')
			player_id = cols[0].a['href'].split('/')[-1]
			stats_dic['player_id'] = player_id
		except TypeError:
			pass

		try:
			cols = row.find_all('td')
			stats_dic['team'] = team
			stats_dic['opponent'] = opponent
			player_position = cols[0].text
			stats_dic['position'] = player_position[-2:]
			stats_dic['player'] = player_position[:-2]
			if player_position[-1] in ('G', 'F', 'C') and  player_position[-2:] not in ('PG', 'SG', 'SF', 'PF', 'C'):
				stats_dic['position'] = player_position[-1:]
				stats_dic['player'] = player_position[:-1]
			stats_dic['home'] = home
			stats_dic['starter'] = starter
			stats_dic['minutes'] = int(cols[1].text)
			stats_dic['fgm'] = int(cols[2].text.split('-')[0])
			stats_dic['fga'] = int(cols[2].text.split('-')[1])
			stats_dic['fg3m'] = int(cols[3].text.split('-')[0])
			stats_dic['fg3a'] = int(cols[3].text.split('-')[1])
			stats_dic['ftm'] = int(cols[4].text.split('-')[0])
			stats_dic['fta'] = int(cols[4].text.split('-')[1])
			stats_dic['oreb'] = int(cols[5].text)
			stats_dic['dreb'] = int(cols[6].text)
			stats_dic['rebounds'] = int(cols[7].text)
			stats_dic['assists'] = int(cols[8].text)
			stats_dic['steals'] = int(cols[9].text)
			stats_dic['blocks'] = int(cols[10].text)
			stats_dic['turnovers'] = int(cols[11].text)
			stats_dic['fouls'] = int(cols[12].text)
			stats_dic['plus_minus'] = int(cols[13].text)
			stats_dic['points'] = int(cols[14].text)
			stats_dic['fp'] = calculateFantasyPoints(stats_dic['points'], stats_dic['fg3m'], stats_dic['rebounds'], stats_dic['assists'], stats_dic['steals'], stats_dic['blocks'], stats_dic['turnovers'])
			stats_dic['played'] = 1
			stats_dic['note'] = None
			stats_array.append(stats_dic)
		except ValueError:
			stats_dic['played'] = 0
			stats_dic['note'] = str(cols[1].text).replace('DNP ', '')
			stats_dic['team'] = team
			stats_dic['opponent'] = opponent
			player_position = cols[0].text
			stats_dic['position'] = player_position[-2:]
			stats_dic['player'] = player_position[:-2]
			if player_position[-1] in ('G', 'F', 'C') and  player_position[-2:] not in ('PG', 'SG', 'SF', 'PF', 'C'):
				stats_dic['position'] = player_position[-1:]
				stats_dic['player'] = player_position[:-1]
			stats_dic['home'] = home
			stats_dic['starter'] = starter
			for stat in ['minutes', 'fgm', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'fouls', 'plus_minus', 'points', 'fp']:
				stats_dic[stat] = 0
			stats_array.append(stats_dic)
	return stats_array



def calculateFantasyPoints(points, fg3m, rebounds, assists, steals, blocks, turnovers):
	fp = float(points) + (float(fg3m)*.5) + (float(rebounds)*1.25) + (float(assists)*1.5) + (float(blocks)*2) + (float(steals)*2) + (float(turnovers)*-.5)
	count = 0
	for stat in [points, rebounds, assists, blocks, steals]:
		if stat >= 10:
			count += 1
	if count == 2:
		fp += 1.5
	if count >= 3:
		fp += 3
	return fp

