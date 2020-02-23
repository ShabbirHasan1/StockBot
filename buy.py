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

MAX_BALANCE = 20000


def removeFromCondition(item):
	df  = utils.readExcel("buywithcondition.xlsx")
	df = df[df['Stock'] != item]
	df.to_excel("buyWithCondition.xlsx",sheet_name='Sheet1',index=False)
	

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
		wb = load_workbook("boughtList.xlsx")
		ws = wb.worksheets[0]
		row_data = [None] * 4
		row_data[0] = item
		row_data[1] = price
		row_data[2] = date.today().strftime('%d %b %Y')
		row_data[3] = qty
		
		status = order.place_order(item, "B", qty)
		if status == 1:
			print 'Buy Item :'+item+' | Qty :'+str(qty)+' | Purchase :'+ str(price)
			balance = utils.getBalance()
			balance = balance - (price*qty)
			utils.saveToFileItem(str(balance), 'balance.txt')
			if qty > 0:
				ws.append(row_data)
				wb.save("boughtList.xlsx")
			return 1
	return 0

def checkCondition(item):
	df  = utils.readExcel("buyWithCondition.xlsx")
	for index, row in df.iterrows():
		if str(row['Stock']) == item:
			currentPrice = getPrice(item)
			print 'checking price'
			if currentPrice < float(row['Cprice']):
				if (buyItem(item, getQty(currentPrice), currentPrice)):
					removeFromCondition(item)
			return 1
	return 0

#buy stock conditions
# 1) The stock status is buy, stock is in buywithcondition excel and the condition is met
# 2) The stock status is buy, stock is not in buy in buywithcondition excel
# 3) Don't buy if stock is already in the boughtList
def main():
	buyList = utils.readText('buy.txt')
	for item in buyList:
		currentPrice = getPrice(item)
		if utils.hasItem(item, "boughtList.xlsx", 'Name'):
			continue
		elif checkCondition(item) == 0:
			buyItem(item, getQty(currentPrice), currentPrice)
			
	df  = utils.readExcel("buyWithCondition.xlsx")
	for index, row in df.iterrows():
		if row['Stock'] not in buyList:
			removeFromCondition(row['Stock'])
			
	print 'buy '+str(buyList)
	
if __name__ == "__main__":
    main()