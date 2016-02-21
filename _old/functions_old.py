from classes import *
teams = []
def valueTeam(team, players):
	if team.underBudget():
		return team
   	
   	players.sort(key=lambda x: x.value, reverse=True)
   	for player in players:
   		diff_list = []
   		for position in [player.position, player.second_position, player.third_position]:
   			diff = player.value - team.team_dic[position].value
			diff_list.append(diff)
			if diff == max(diff_list):
				position_out = position
		if player.name not in team.getPlayers() and max(diff_list) > 0:
			sub = player
			new_team = team
			new_team.team_dic[position_out] = sub
			new_team = Team(new_team.team_dic)
			players.remove(sub)
			return valueTeam(new_team, players)

optimal_teams = []
def optimizeTeam(team, players):
	global optimal_teams
	for player in players:
		if player.name not in team.getPlayers():
			for position in [player.position, player.second_position, player.third_position]:
				if player.pfp > team.team_dic[position].pfp:
					sub = player
					position_out = position
					new_team = team
					new_team.team_dic[position_out] = sub
					new_team = Team(new_team.team_dic)
					if new_team.underBudget():
						optimal_teams.append(new_team)
				else:
					if player.value > team.team_dic[position].value and player.salary < team.team_dic[position].salary:
						sub = player
						position_out = position
						new_team = team
						new_team.team_dic[position_out] = sub
						new_team = Team(new_team.team_dic)
						players.remove(team.team_dic[position_out])
						return optimizeTeam(new_team, players)
	return optimal_teams

max_teams = []
def maxTeams(team, players):
	players.sort(key=lambda x: x.pfp, reverse=True)
	global max_teams
	if team.underBudget():
		max_teams.append(team)
	new_players = []
	for player in players:
		if player.name not in team.getPlayers():
			diff_list = []
			for position in [player.position, player.second_position, player.third_position]:
				diff = team.team_dic[position].pfp - player.pfp
				diff_list.append(diff)
				if diff == min(diff_list):
					player.diff = diff
					player.position_out = position
			if player.diff > 0:
				new_players.append(player)
	new_players.sort(key=lambda x: x.diff)
	for player in new_players[:8]:
		new_team = team
		new_team.team_dic[player.position_out] = player
		new_team = Team(new_team.team_dic)
		players.remove(team.team_dic[player.position_out])
		if new_team.underBudget():
			print new_team
		return maxTeams(new_team, new_players)
	return max_teams

		
				










