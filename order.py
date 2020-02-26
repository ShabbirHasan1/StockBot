import logging
from kiteconnect import KiteConnect
import utils
import time
import re
import requests
import urlparse
logging.basicConfig(level=logging.DEBUG)

#kite = KiteConnect(api_key="6m485o0cpsicqsw7")

kite = KiteConnect(api_key="6m485o0cpsicqsw7", access_token="FTmbZTO3rmk3Sjls1ttPAC1vzgjGJEVT")
#kite.renew_access_token("a30N8alKxnzUeEqjTh5XJAgBgIbV9kHH", "2h2k6kqpio3xyigxtlor49pcx1g6ofoo")

#data = kite.generate_session("4jjsuRaf6b6Skv2TO533NMzx5Ga0BtnT", api_secret="2h2k6kqpio3xyigxtlor49pcx1g6ofoo")
#print data["access_token"]
#kite.set_access_token(data["access_token"])


def getMappedSymbol(stock):
	df = utils.readExcel('stock-unique.xlsx')
	for index, row in df.iterrows():
		if row['id'] == stock:
			return row['Symbol']
		
	return

def place_order(stock, type, qty):

	symbol = getMappedSymbol(stock)
	if type == "B":
		trans = kite.TRANSACTION_TYPE_BUY
	if type == "S":
		trans = kite.TRANSACTION_TYPE_SELL
	
	# Place an order
	try:
		order_id = kite.place_order(tradingsymbol=symbol, exchange=kite.EXCHANGE_NSE,transaction_type=trans,quantity=qty,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_CNC, variety=kite.VARIETY_REGULAR)
	
		logging.info("Order placed. ID is: {}".format(order_id))
		logging.info("Order placed: {}".format(str(symbol) + " | "+str(type)+" | "+ str(qty)))
		#print 'order placed'
		return 1
	except Exception as e:
		logging.info("Order placement failed: {}".format(e.message))
		return 0
# Fetch all orders
#kite.orders()

def getInstruments():
	# Get instruments
	return kite.instruments()
	

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