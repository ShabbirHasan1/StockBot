#import MySQLdb
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from datetime import date
from db_connector import db_connector
#conn = MySQLdb.connect(host='fdb17.runhosting.com', user='sukrit.raghuvanshi1990', passwd='Crashing@1', db='3337075_stock')

#def close():
#	cursor.close()
#	conn.close()

@db_connector
def upsertList(conn, table, items):
	cursor = conn.cursor()
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

@db_connector
def upsertsingle(conn, table, items):
	cursor = conn.cursor()
	#var_string = ', '.join('?' * len(items))
	#query_string = 'REPLACE INTO '+ table+ ' VALUES (%s);' % var_string
	query_string = "REPLACE INTO "+ table+" VALUES %s;" % (tuple(items),)
	print query_string
	#cursor.executemany(query_string, items)
	cursor.execute(query_string)
	conn.commit()
	
@db_connector
def upsert(conn, table, items):
	cursor = conn.cursor()
	#var_string = ', '.join('?' * len(items))
	#query_string = 'REPLACE INTO '+ table+ ' VALUES (%s);' % var_string
	query_string = "REPLACE INTO "+ table+" VALUES %s;" % (tuple(items),)
	print query_string
	cursor.executemany(query_string, items)
	conn.commit()
	
@db_connector
def read(conn, table):
	query_string = "SELECT * FROM "+ table
	df = pd.read_sql_query(query_string, conn)
	#print(df)
	return df

@db_connector
def readItemWhere(conn, table, column, id):
	df = read(table)
	for index, row in df.iterrows():
		if row['id'] == id:
			print 'returning value :'+ str(row[column])
			return str(row[column])

@db_connector
def readItem(conn, table, column, column2, item2):
	df = readAll(table, column2, item2)
	for index, row in df.iterrows():
		if index == 0:
			print 'returning value :'+ str(row[column])
			return str(row[column])

@db_connector
def readAll(conn, table, column, item):
	query_string = "SELECT * FROM "+table+" WHERE "+ column+ " = "+str(item)+""
	df = pd.read_sql_query(query_string, conn)
	return df

@db_connector
def delete(conn, table, column, item, column2, item2):
	cursor = conn.cursor()
	query_string = "DELETE FROM "+ table+" WHERE "+column+" = '"+str(item)+"'"+ " AND "+column2+" = "+str(item2)
	print query_string
	cursor.execute(query_string, item)
	conn.commit()

@db_connector
def hasItem(conn, item1, item2, table, column1, column2):
	query_string = "SELECT * FROM "+table+" WHERE "+ column1+ " = '"+item1+"'"+" AND "+ column2+ " = "+str(item2)
	print query_string
	df = pd.read_sql_query(query_string, conn)
	if df.size > 0:
		return True
	else:
		return False
























