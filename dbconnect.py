#import MySQLdb
import mysql.connector
from mysql.connector import errorcode
#conn = MySQLdb.connect(host='fdb17.runhosting.com', user='sukrit.raghuvanshi1990', passwd='Crashing@1', db='3337075_stock')
try:
	conn = mysql.connector.connect(host='sql7.freemysqlhosting.net', user='sql7324930', password='WRjxg65nmp', database='sql7324930')
except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
	else:
		print(err)
else:
	cursor = conn.cursor()

	#cursor.execute("SELECT COUNT(*) FROM `TABLE 1`")
	#row = cursor.fetchone()

	#conn.close()

	#print(row)
	
	
def upsert(table, items):
	var_string = ', '.join('?' * len(items))
	#query_string = 'REPLACE INTO '+ table+ ' VALUES (%s);' % var_string
	query_string = "REPLACE INTO "+ table+" VALUES %r;" % (tuple(items),)
	#print query_string
	cursor.execute(query_string, items)




























