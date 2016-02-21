import requests, json, MySQLdb, itertools
from datetime import datetime, date
from bs4 import BeautifulSoup
import pandas as pd

class ESPN:
	def __init__(self):
		self.base_url = 'http://espn.go.com/'
		self.games = 'nba/team/schedule/_/name/'
		self.year = '2016'
		self.games_array = []
	
	def getTeams(self):
		url = self.base_url + 'nba/teams'
		r = requests.get(url)
		soup = BeautifulSoup(r.text)
		tables = soup.find_all('ul', class_='medium-logos')
		teams = []
		for table in tables:
		    lis = table.find_all('li')
		    for li in lis:
		    	team_dic = {}
		        info = li.h5.a
		        team = info.text
		        team_dic['team'] = team
		        url = info['href']
		        team_dic['url'] = url
		        city = url.split('/')[-2]
		        team_dic['city'] = city
		        prefix = url.split('/')[-1]
		        team_dic['prefix'] = prefix
		     	teams.append(team_dic)
		return teams


	def getGames(self):
		teams = self.getTeams()
		for row in teams[:1]:
			team = row['team']
			city = row['city']
			prefix = row['prefix']
			url = self.base_url + self.games + city + '/' + self.year + '/' + prefix
			r = requests.get(url)
			table = BeautifulSoup(r.text).table
			print table.find_all('tr')[1:]
			for next_row in table.find_all('tr')[1:]:
				game_dic = {}
		    	columns = next_row.find_all('td') 	
		    	try:
		    		match_id = columns[2].a['href'].split('?id=')[1]
		    		print match_id
		    	except Exception:
		    		pass
		    	

		    		# match_id = columns[2].a['href'].split('?id=')[1]
		    		# game_dic['match_id'] = match_id
		    		# score = columns[2].a.text.split(' ')[0].split('-')
		    		# d = datetime.strptime(columns[0].text, '%a, %b %d')
		    		# if d.month < 10:
		    		# 	game_date = date(int(self.year), d.month, d.day)
		    		# if d.month >= 10:
		    		# 	game_date = date(int(self.year)-1, d.month, d.day)
		    		# game_dic['date'] = game_date
		    		# if columns[1].li.text == 'vs':
		    		# 	game_dic['home_team'] = team
		    		# 	game_dic['away_team'] = columns[1].find_all('a')[1].text
		    		# 	if columns[2].span.text == 'W':
		    		# 		game_dic['home_team_score'] = score[0]
		    		# 		game_dic['away_team_score'] = score[1]
		    		# 	else:
		    		# 		game_dic['home_team_score'] = score[1]
		    		# 		game_dic['away_team_score'] = score[0]
		    		# if columns[1].li.text != 'vs':
		    		# 	game_dic['home_team'] = columns[1].find_all('a')[1].text
		    		# 	game_dic['away_team'] = team
		    		# 	if columns[2].span.text == 'W':
		    		# 		game_dic['home_team_score'] = score[1]
		    		# 		game_dic['away_team_score'] = score[0]
		    		# 	else:
		    		# 		game_dic['home_team_score'] = score[0]
		    		# 		game_dic['away_team_score'] = score[1]
		    		# print game_dic['date'], game_dic['home_team']
		
		#     	except Exception:
		#     		try:
		#     			match_id = columns[2].a['href'].split('?id=')[1]
		#     			game_dic['match_id'] = match_id
		#     			d = datetime.strptime(columns[0].text, '%a, %b %d')
		#     			if d.month < 10:
		#     				game_date = date(int(self.year), d.month, d.day)
		#     			if d.month >= 10:
		#     				game_date = date(int(self.year)-1, d.month, d.day)
		#     			if columns[1].li.text == 'vs':
		#     				game_dic['home_team'] = team
		#     				game_dic['away_team'] = columns[1].find_all('a')[1].text
		#     			if columns[1].li.text != 'vs':
		#     				game_dic['home_team'] = columns[1].find_all('a')[1].text
		#     				game_dic['away_team'] = team
		#     			game_dic['home_team_score'] = None
		#     			game_dic['away_team_score'] = None
		#     			game_dict['date'] = game_date
						
		#     		except Exception:
		#     			pass
		# db.commit()
		# db.close()

espn = ESPN()
espn.getGames()

		 









