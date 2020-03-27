import mysql.connector
import logging
def db_connector5(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='bd70a07d2c411d', password='830accfd', database='heroku_7f2b92b3739a0fa')
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