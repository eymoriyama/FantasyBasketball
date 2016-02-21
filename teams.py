import MySQLdb
from espnmanager import *

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
cursor.execute("DELETE FROM teams")

espn = ESPN()
teams_array = espn.getTeams()
print teams_array

for row in teams_array:
	cursor.executemany("INSERT INTO teams (team, url, city, prefix) VALUES (%s, %s, %s,  %s)",
	[(row['team'], row['url'], row['city'], row['prefix'])])

db.commit()
db.close()