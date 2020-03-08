import mysql.connector
import logging
def db_connector4(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='us-cdbr-iron-east-04.cleardb.net', user='b19e97907589ed', password='b989c676', database='heroku_f391e330243d01e')
		try:
			rv = func(cnn, *args,**kwargs)
		except Exception:
			cnn.rollback()
			logging.error("Database connection error")
			raise
		else:
			cnn.commit()
		finally:
			cnn.close()
		return rv
	return with_connection_