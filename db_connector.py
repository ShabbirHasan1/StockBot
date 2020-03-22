import mysql.connector
import logging
def db_connector(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='us-cdbr-iron-east-04.cleardb.net', user='b1f7a97fa97a65', password='6a0a1fd5', database='heroku_9a3f1be26cdc376')
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
