#import MySQLdb
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
#conn = MySQLdb.connect(host='fdb17.runhosting.com', user='sukrit.raghuvanshi1990', passwd='Crashing@1', db='3337075_stock')
try:
	conn = mysql.connector.connect(host='sql12.freemysqlhosting.net', user='sql12324946', password='JXdDfG3ZBD', database='sql12324946')
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
	
def close():
	cursor.close()
	conn.close()
	
def upsert(table, items):
	#var_string = ', '.join('?' * len(items))
	#query_string = 'REPLACE INTO '+ table+ ' VALUES (%s);' % var_string
	query_string = "REPLACE INTO "+ table+" VALUES %s;" % (tuple(items),)
	print query_string
	cursor.executemany(query_string, items)
	conn.commit()
	
def read(table):
	query_string = "SELECT * FROM "+ table
	df = pd.read_sql_query(query_string, conn)
	#print(df)
	return df




























