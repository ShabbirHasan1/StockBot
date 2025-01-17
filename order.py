import logging
from kiteconnect import KiteConnect
import utils
import time
import re
import requests
import urlparse
import dbconnect
import dbconnect5
logging.basicConfig(level=logging.DEBUG)

#token = str(utils.readText('access_token.txt')[0])
STATUS = 'INACTIVE'

	
def getMappedSymbol(stock):
	df = utils.readExcel('stock-unique.xlsx')
	for index, row in df.iterrows():
		if row['id'] == stock:
			return row['Symbol']
		
	return


def getNSESymbol(stock):
	return dbconnect.readItemWhere('stock', 'nseid', stock)


def place_order(stock, type, qty, id):
	token = dbconnect.readItem('TOKEN', 'VALUE', "ID", id)
	acctType = dbconnect.readItem('ACCOUNT','TYPE','ID',id)
	kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
	symbol = getNSESymbol(stock)
	if type == "B":
		trans = kite.TRANSACTION_TYPE_BUY
	if type == "S":
		trans = kite.TRANSACTION_TYPE_SELL
	
	if utils.checkQuantity(stock, type):
		# Place an order
		try:
			if (acctType=='LIVE'):
				if (STATUS=='ACTIVE'):
					order_id = kite.place_order(tradingsymbol=symbol, exchange=kite.EXCHANGE_NSE,transaction_type=trans,quantity=qty,order_type=kite.ORDER_TYPE_MARKET,roduct=kite.PRODUCT_CNC, variety=kite.VARIETY_REGULAR)			
					logging.info("Order placed. ID is: {}".format(order_id))
					logging.info("Order placed: {}".format(str(symbol) + " | "+str(type)+" | "+ str(qty)))
					print 'order placed'
					return 1
				else:
					utils.sendSMS2(str(type)+" ", str(symbol)+" "+str(qty))
					return 1
			else:
				logging.info("Order placed: {}".format(str(symbol) + " | "+str(type)+" | "+ str(qty)))
				print 'order placed'
				return 1
		except Exception as e:
				logging.info("Order placement failed: {}".format(e.message))
				return 0
	else:
		logging.info("Order placement failed: Quantity not satisfied")
		return 0
# Fetch all orders
#kite.orders()

def getInstruments(id):
	token = dbconnect.readItem('TOKEN', 'VALUE', "ID", id)
	kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
	# Get instruments
	return kite.instruments()
	
def getHoldings(id):
	token = dbconnect.readItem('TOKEN', 'VALUE', "ID", id)
	kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
	# Get instruments
	try: 
		return kite.holdings()
	except Exception as e:
		token = dbconnect.readItem('TOKEN', 'VALUE', "ID", "1")
		kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
		return kite.holdings()

# Place an mutual fund order
#kite.place_mf_order(
#    tradingsymbol="INF090I01239",
#    transaction_type=kite.TRANSACTION_TYPE_BUY,
#    amount=5000,
#    tag="mytag"
#)

# Cancel a mutual fund order
#kite.cancel_mf_order(order_id="order_id")

# Get mutual fund instruments
#kite.mf_instruments()
