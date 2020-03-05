from pprint import pprint
import numpy as np
import pandas as pd
import csv
import json 
import requests
from datetime import datetime
from collections import Counter
from datetime import date
from my_dictionary import my_dictionary
from notify_run import Notify
from openpyxl import load_workbook
import os
import xlrd
import utils
import order
import dbconnect

MAX_BALANCE = 20000


def removeFromCondition(item):
	dbconnect.delete('CONDITION_BUY', 'STOCK', item)
	#df  = utils.readExcel("buywithcondition.xlsx")
	#df = df[df['Stock'] != item]
	#df.to_excel("buyWithCondition.xlsx",sheet_name='Sheet1',index=False)
	

def getQty(price):
	#balance = float(str(utils.getBalance()))
	alBalance = MAX_BALANCE/6.0
	return int(alBalance/price)

def getPrice(item):
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}
	url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+item
	rcomp = requests.get(url, headers=headers)
	data = json.loads(rcomp.text)
	currentPrice = float(str(data['graph']['current_close']))
	return currentPrice

def buyItem(item, qty, price):
	if utils.getBalance() > 0:
		print 'Buying item'
		#wb = load_workbook("boughtList.xlsx")
		#ws = wb.worksheets[0]
		row_data = [None] * 5
		row_data[0] = '1'
		row_data[1] = str(item)
		row_data[2] = price
		row_data[3] = date.today().strftime('%d %b %Y')
		row_data[4] = qty
		
		status = order.place_order(item, "B", qty)
		if status == 1:
			print 'Buy Item :'+item+' | Qty :'+str(qty)+' | Purchase :'+ str(price)
			balance = utils.getBalance()
			balance = balance - (price*qty)
			dbconnect.upsert("BALANCE", ('1', str(balance)) )
			#utils.saveToFileItem(str(balance), 'balance.txt')
			if qty > 0:
				#ws.append(row_data)
				#wb.save("boughtList.xlsx")
				dbconnect.upsert("BOUGHT_LIST", row_data)
			return 1
	return 0

def checkCondition(item):
	#df  = utils.readExcel("buyWithCondition.xlsx")
	df = dbconnect.read('CONDITION_BUY')
	for index, row in df.iterrows():
		if str(row['STOCK']) == item:
			currentPrice = getPrice(item)
			print 'checking price'
			if currentPrice < float(row['CPRICE']):
				if (buyItem(item, getQty(currentPrice), currentPrice)):
					removeFromCondition(item)
			return 1
	return 0

#buy stock conditions
# 1) The stock status is buy, stock is in buywithcondition excel and the condition is met
# 2) The stock status is buy, stock is not in buy in buywithcondition excel
# 3) Don't buy if stock is already in the boughtList
def main():
	#buyList = utils.readText('buy.txt')
	buyDf = dbconnect.read("BUY")
	temp_list = []
	for index, row in buyDf.iterrows():
		if index == 0:
			temp_list = [row.ITEM1, row.ITEM2, row.ITEM3, row.ITEM4, row.ITEM5]
	for item in temp_list:
		currentPrice = getPrice(item)
		if dbconnect.hasItem(item, "BOUGHT_LIST", 'NAME'):
			continue
		elif checkCondition(item) == 0:
			buyItem(item, getQty(currentPrice), currentPrice)
			
	#df  = utils.readExcel("buyWithCondition.xlsx")
	df = dbconnect.read("CONDITION_BUY")
	for index, row in df.iterrows():
		if row['STOCK'] not in temp_list:
			dbconnect.delete("CONDITION_BUY", "STOCK", row['STOCK'])
			#removeFromCondition(row['Stock'])
			
	print 'buy '+str(temp_list)
	
if __name__ == "__main__":
    main()