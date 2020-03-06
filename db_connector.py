import mysql.connector
import logging
def db_connector(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='sql12.freemysqlhosting.net', user='sql12324997', password='vFiJPaxjy6', database='sql12324997')
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

