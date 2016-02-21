
def getBudget(team, salary_dict):
	pg_salary = float(salary_dict[team['pg']]) 
	sg_salary = float(salary_dict[team['sg']]) 
	sf_salary = float(salary_dict[team['sf']]) 
	pf_salary = float(salary_dict[team['pf']]) 
	c_salary = float(salary_dict[team['c']])
	g_salary = float(salary_dict[team['g']])
	f_salary = float(salary_dict[team['f']])
	u_salary = float(salary_dict[team['u']])
	budget = pg_salary + sg_salary + sf_salary + pf_salary + c_salary + g_salary + f_salary + u_salary
	return budget


def calculateBudget(team, salary_dict):
	budget = 0
	for player in team:
		budget += salary_dict[player]
	return budget


def calculatePFP(team, pfp_dict):
	pfp = 0
	for player in team:
		pfp += pfp_dict[player]
	return pfp	

def getTotalPoints(team, appg_dict):
	pg_appg = float(appg_dict[team['pg']]) 
	sg_appg = float(appg_dict[team['sg']]) 
	sf_appg = float(appg_dict[team['sf']]) 
	pf_appg = float(appg_dict[team['pf']]) 
	c_appg = float(appg_dict[team['c']])
	g_appg = float(appg_dict[team['g']])
	f_appg = float(appg_dict[team['f']])
	u_appg = float(appg_dict[team['u']])
	total_points = pg_appg + sg_appg + sf_appg + pf_appg + c_appg + g_appg + f_appg + u_appg
	return total_points


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



def updateInfo(info):
	if info == '':
		return None
	else:
		return info

def updateStat(stat):
	if stat == '':
		return 0
	else:
		return stat	

def updateMinutes(minutes):
	mins = int(minutes[:len(minutes)-3])
	secs = int(minutes[len(minutes)-2:]) 
	if secs >= 60:
		mins = int(minutes[:len(minutes)-3]) + 1
		secs = secs - 60
		minutes = str(mins) + ':' + str(secs)
	return minutes


def getOptimalTeam(team, bench, salary_dict, fp_dict):
	budget = getBudget(team, salary_dict)
	fp = getTotalPoints(team, fp_dict)
	if budget <= 50000.0:
		print tuple(team.values()), fp, budget
	
	diff_dict = {}
	for position in list(bench.keys()):
		starter = team[position]
		sub = bench[position][0]
		fp_diff = fp_dict[starter] - fp_dict[sub]
		salary_diff = salary_dict[starter] - salary_dict[sub] 
		if salary_diff > 0.0 and fp_diff > 0:
			diff_dict[position] = fp_diff

	diff_list = list(diff_dict.values())
	diff_list.sort()
	if len(diff_list) == 0:
		for position in list(bench.keys()):
			out = bench[position][0]
			bench[position].remove(out)
		return getOptimalTeam(team, bench, salary_dict, fp_dict)
	
	for diff in diff_list:
		for position in list(diff_dict.keys()):
			if diff_dict[position] == diff:
				out = team[position]
				sub =  bench[position][0]
				team[position] = sub
				if getBudget(team, salary_dict) <= 50000:
					budget = getBudget(team, salary_dict)
					fp = getTotalPoints(team, fp_dict)
					return tuple(team.values()), fp, budget
				else:
					team[position] = out
	position_out = min(diff_dict, key=lambda k: diff_dict[k])
	sub = bench[position_out][0]
	team[position_out] = sub
	for position in list(bench.keys()):
		players = bench[position]
		try:
			players.remove(sub)
		except ValueError:
			pass			
	return getOptimalTeam(team, bench, salary_dict, fp_dict)



def getOptimalTeamv2(team, bench, salary_dict, fp_dict, reserves={}):
	budget = getBudget(team, salary_dict)
	fp = getTotalPoints(team, fp_dict)
	if budget <= 50000.0:
		return {'team': tuple(team.values()), 'pfp': fp, 'budget': budget}

	for position in list(bench.keys()):
		if len(bench[position]) == 0:
			del bench[position]

	diff_dict = {}
	for position in list(bench.keys()):
		starter = team[position]
		sub = bench[position][0]
		fp_diff = fp_dict[starter] - fp_dict[sub]
		salary_diff = salary_dict[starter] - salary_dict[sub] 
		if salary_diff > 0.0 and fp_diff > 0:
			diff_dict[position] = fp_diff
	diff_list = list(diff_dict.values())
	diff_list.sort()
	
	if len(diff_list) == 0:
		for position in list(bench.keys()):
			out = bench[position][0]
			bench[position].remove(out)
		return getOptimalTeamv2(team, bench, salary_dict, fp_dict, reserves)


	for position in list(reserves.keys()):
		out = team[position]
		sub = reserves[position]
		team[position] = sub	
		if getBudget(team, salary_dict) <= 50000:
			budget = getBudget(team, salary_dict)
			fp = getTotalPoints(team, fp_dict)
			return {'team': tuple(team.values()), 'pfp': fp, 'budget': budget}

		for diff in diff_list:
			for next_position in list(diff_dict.keys()):
				if diff_dict[next_position] == diff:
					next_out = team[next_position]
					next_sub =  bench[next_position][0]
					team[next_position] = next_sub
					if getBudget(team, salary_dict) <= 50000:
						budget = getBudget(team, salary_dict)
						fp = getTotalPoints(team, fp_dict)
						return {'team': tuple(team.values()), 'pfp': fp, 'budget': budget}
					else:
						team[next_position] = next_out
		team[position] = out

	for diff in diff_list:
		for position in list(diff_dict.keys()):
			if diff_dict[position] == diff:
				out = team[position]
				sub =  bench[position][0]
				team[position] = sub
				if getBudget(team, salary_dict) <= 50000:
			 		budget = getBudget(team, salary_dict)
					fp = getTotalPoints(team, fp_dict)
					return {'team': tuple(team.values()), 'pfp': fp, 'budget': budget}
				else:
					team[position] = out
	position_out = min(diff_dict, key=lambda k: diff_dict[k])
	sub = bench[position_out][0]
	team[position_out] = sub
	reserves[position_out] = sub
	for position in list(bench.keys()):
		players = bench[position]
		try:
			players.remove(sub)
		except ValueError:
			pass			
	return getOptimalTeamv2(team, bench, salary_dict, fp_dict, reserves)

def getOptimalTeamv3(team, bench, salary_dict, fp_dict, reserves={}):
	max_points = 0
	while True:
		print team
		budget = getBudget(team, salary_dict)
		fp = getTotalPoints(team, fp_dict)
		if budget <= 50000.0 and fp > max_points:
			optimal_team = team
			max_points = fp



		for position in list(bench.keys()):
			if len(bench[position]) == 0:
				return optimal_team

		diff_dict = {}
		for position in list(bench.keys()):
			starter = team[position]
			sub = bench[position][0]
			fp_diff = fp_dict[starter] - fp_dict[sub]
			salary_diff = salary_dict[starter] - salary_dict[sub] 
			diff_dict[position] = fp_diff
		
		diff_list = list(diff_dict.values())
		diff_list.sort()

		for position in list(reserves.keys()):
			for player in reserves[position]:
				out = team[position]
				sub = player
				team[position] = sub
				budget = getBudget(team, salary_dict)
				fp = getTotalPoints(team, fp_dict)
				if budget <= 50000.0 and fp > max_points:
					optimal_team = team
					max_points = fp
				for diff in diff_list:
					for next_position in list(diff_dict.keys()):
						if diff_dict[next_position] == diff:
							next_out = team[next_position]
							next_sub =  bench[next_position][0]
							team[next_position] = next_sub
							if budget <= 50000.0 and fp > max_points:
								optimal_team = team
								max_points = fp
							team[next_position] = next_out
				team[position] = out

		for diff in diff_list:
			for position in list(diff_dict.keys()):
				if diff_dict[position] == diff:
					out = team[position]
					sub =  bench[position][0]
					team[position] = sub
					if budget <= 50000.0 and fp > max_points:
						optimal_team = team
						max_points = fp
					team[position] = out
		position_out = min(diff_dict, key=lambda k: diff_dict[k])
		sub = bench[position_out][0]
		team[position_out] = sub
		reserves[position_out].append(sub)
		for position in list(bench.keys()):
			players = bench[position]
			try:
				players.remove(sub)
			except ValueError:
				pass


