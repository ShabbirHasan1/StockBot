import mysql.connector
import logging
def db_connector3(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='us-cdbr-iron-east-04.cleardb.net', user='b8538395691ab6', password='cf93de96', database='heroku_fd9c772e422f001')
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