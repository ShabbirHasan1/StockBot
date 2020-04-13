import mysql.connector
import logging
def db_connector_new(func):
	def with_connection_(*args,**kwargs):
		cnn = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b865f30025a702', password='302c55ae', database='heroku_25570552915163b')
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
