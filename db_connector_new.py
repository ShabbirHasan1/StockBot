import mysql.connector
import logging
def db_connector_new(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='us-cdbr-iron-east-04.cleardb.net', user='b3386ea5051315', password='dbe2db2d', database='heroku_6080183310e92dc')
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

