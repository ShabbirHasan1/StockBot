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

token = dbconnect.readItem('TOKEN', 'VALUE')
kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
	
def getMappedSymbol(stock):
	df = utils.readExcel('stock-unique.xlsx')
	for index, row in df.iterrows():
		if row['id'] == stock:
			return row['Symbol']
		
	return


def getNSESymbol(stock):
	return dbconnect5.readItemWhere('stock', 'nseid', stock)


def place_order(stock, type, qty):
	token = dbconnect.readItem('TOKEN', 'VALUE')
	kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
	symbol = getNSESymbol(stock)
	if type == "B":
		trans = kite.TRANSACTION_TYPE_BUY
	if type == "S":
		trans = kite.TRANSACTION_TYPE_SELL
	
	# Place an order
	try:
		order_id = kite.place_order(tradingsymbol=symbol, exchange=kite.EXCHANGE_NSE,transaction_type=trans,quantity=qty,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_CNC, variety=kite.VARIETY_REGULAR)
	
		logging.info("Order placed. ID is: {}".format(order_id))
		logging.info("Order placed: {}".format(str(symbol) + " | "+str(type)+" | "+ str(qty)))
		print 'order placed'
		return 1
	except Exception as e:
		try:
			token = dbconnect.readItem('TOKEN', 'VALUE')
			kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token=token)
			order_id = kite.place_order(tradingsymbol=symbol, exchange=kite.EXCHANGE_NSE,transaction_type=trans,quantity=qty,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_CNC, variety=kite.VARIETY_REGULAR)
	
			logging.info("Order placed. ID is: {}".format(order_id))
			logging.info("Order placed: {}".format(str(symbol) + " | "+str(type)+" | "+ str(qty)))
			print 'order placed'
			return 1
		except Exception as e:
			logging.info("Order placement failed: {}".format(e.message))
			return 0
# Fetch all orders
#kite.orders()

def getInstruments():
	# Get instruments
	return kite.instruments()
	
def getHoldings():
	# Get instruments
	try: 
		return kite.holdings()
	except Exception as e:
		token = dbconnect.readItem('TOKEN', 'VALUE')
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
