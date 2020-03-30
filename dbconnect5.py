#import MySQLdb
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from datetime import date
from db_connector5 import db_connector5


@db_connector5
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

@db_connector5
def upsertsingle(conn, table, items):
	cursor = conn.cursor()
	#var_string = ', '.join('?' * len(items))
	#query_string = 'REPLACE INTO '+ table+ ' VALUES (%s);' % var_string
	query_string = "REPLACE INTO "+ table+" VALUES %s;" % (tuple(items),)
	print query_string
	#cursor.executemany(query_string, items)
	cursor.execute(query_string)
	conn.commit()
	
@db_connector5
def upsert(conn, table, items):
	cursor = conn.cursor()
	#var_string = ', '.join('?' * len(items))
	#query_string = 'REPLACE INTO '+ table+ ' VALUES (%s);' % var_string
	query_string = "REPLACE INTO "+ table+" VALUES %s;" % (tuple(items),)
	print query_string
	cursor.executemany(query_string, items)
	conn.commit()
	
@db_connector5
def read(conn, table):
	query_string = "SELECT * FROM "+ table
	df = pd.read_sql_query(query_string, conn)
	#print(df)
	return df

@db_connector5
def readItem(conn, table, column):
	df = read(table)
	for index, row in df.iterrows():
		if index == 0:
			print 'returning value :'+ str(row[column])
			return str(row[column])

@db_connector5
def readItemWhere(conn, table, column, id):
	df = read(table)
	for index, row in df.iterrows():
		if row['id'] == id:
			print 'returning value :'+ str(row[column])
			return str(row[column])

@db_connector5
def delete(conn, table, column, item):
	cursor = conn.cursor()
	query_string = "DELETE FROM "+ table+" WHERE "+column+" = '"+str(item)+"'"
	print query_string
	cursor.execute(query_string, item)
	conn.commit()

@db_connector5
def hasItem(conn, item, table, column):
	query_string = "SELECT * FROM "+table+" WHERE "+ column+ " = '"+item+"'"
	df = pd.read_sql_query(query_string, conn)
	if df.size > 0:
		return True
	else:
		return False
























