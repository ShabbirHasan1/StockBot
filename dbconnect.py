#import MySQLdb
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from datetime import date
#conn = MySQLdb.connect(host='fdb17.runhosting.com', user='sukrit.raghuvanshi1990', passwd='Crashing@1', db='3337075_stock')
try:
	conn = mysql.connector.connect(host='sql12.freemysqlhosting.net', user='sql12324997', password='vFiJPaxjy6', database='sql12324997')
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

def upsertList(table, items):
	today =  str(date.today().strftime('%d %b %Y'))
	text = ""
	for item in items:
		text = text + "'"+str(item)+"'" + ','
	text = text[:-1]
	#items.insert(0,1)
	
	query_string = "REPLACE INTO "+ table + " VALUES (1,'"+ today+"',"+text+")"
	print query_string
	cursor.execute(query_string)
	conn.commit()

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

def readItem(table, column):
	df = read(table)
	for index, row in df.iterrows():
		if index == 0:
			print 'returning value :'+ str(row[column])
			return str(row[column])


def delete(table, column, item):
	query_string = "DELETE FROM "+ table+" WHERE "+column+" = '"+str(item)+"'"
	print query_string
	cursor.execute(query_string, item)
	conn.commit()

def hasItem(item, table, column):
	query_string = "SELECT * FROM "+table+" WHERE "+ column+ " = '"+item+"'"
	df = pd.read_sql_query(query_string, conn)
	if df.size > 0:
		return True
	else:
		return False
























