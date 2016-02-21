import MySQLdb, itertools, requests, json, datetime
from datetime import timedelta


db = MySQLdb.Connect("127.0.0.1", "root", "", "Draft Kings")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;') 
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

cursor.execute("SELECT * FROM salarydata")
column_names = [col[0] for col in cursor.description]
data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
db.commit()
db.close()

db = MySQLdb.Connect("127.0.0.1", "root", "", "NBA Data")
cursor = db.cursor()

print "INSERTING"
for row in data:
	cursor.executemany("INSERT INTO salarydata (date, player, salary) VALUES (%s, %s, %s)", [(row['date'], row['player_name'], row['salary'])])

db.commit()
db.close()