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


def getFund(id):
	return float(dbconnect.readItem('BALANCE', 'FUND', 'ID', id))

def getInitial(id):
	return float(dbconnect.readItem('BALANCE', 'INITIAL', 'ID', id))

def removeFromCondition(item, id):
	#dbconnect.delete('CONDITION_BUY', 'STOCK', item)
	dbconnect.delete("CONDITION_BUY", "STOCK", item, "ID", id)
	#df  = utils.readExcel("buywithcondition.xlsx")
	#df = df[df['Stock'] != item]
	#df.to_excel("buyWithCondition.xlsx",sheet_name='Sheet1',index=False)
	

def getQty(price, id):
	#balance = float(str(utils.getBalance()))
	alBalance = getInitial(id)/6.0
	return int(alBalance/price)

def getPrice(item):
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}
	url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+item
	rcomp = requests.get(url, headers=headers)
	data = json.loads(rcomp.text)
	currentPrice = float(str(data['graph']['current_close']))
	return currentPrice

def buyItem(item, qty, price, id):
	initial = getInitial(id)
	if getFund(id) > initial/6.0:
		print 'Buying item'
		#wb = load_workbook("boughtList.xlsx")
		#ws = wb.worksheets[0]
		row_data = [None] * 5
		row_data[0] = str(id)
		row_data[1] = str(item)
		row_data[2] = price
		row_data[3] = date.today().strftime('%d %b %Y')
		row_data[4] = qty
		
		status = order.place_order(item, "B", qty, id)
		if status == 1:
			price = utils.getZerodhaPrice(price, qty, "B")
			print 'Buy Item :'+item+' | Qty :'+str(qty)+' | Purchase :'+ str(price)
			balance = utils.getFund(id)
			balance = balance - (price*qty)
			
			#utils.saveToFileItem(str(balance), 'balance.txt')
			if qty > 0:
				#ws.append(row_data)
				#wb.save("boughtList.xlsx")
				dbconnect.upsert("BALANCE", (str(id), str(balance), str(initial)) )
				dbconnect.upsert("BOUGHT_LIST", row_data)
				dbconnect.upsert("LOG", (str(id), str(item), str(qty), str(price), str(date.today().strftime('%d %b %Y')), "B" ))
			return 1
	return 0

def checkCondition(item, id):
	#df  = utils.readExcel("buyWithCondition.xlsx")
	df = dbconnect.readAll('CONDITION_BUY','id', id)
	for index, row in df.iterrows():
		if str(row['STOCK']) == item:
			currentPrice = getPrice(item)
			print 'checking price'
			if currentPrice < float(row['CPRICE']):
				if (buyItem(item, getQty(currentPrice, id), currentPrice, id)):
					removeFromCondition(item, id)
			return 1
	return 0

#buy stock conditions
# 1) The stock status is buy, stock is in buywithcondition excel and the condition is met
# 2) The stock status is buy, stock is not in buy in buywithcondition excel
# 3) Don't buy if stock is already in the boughtList
def main():
	#buyList = utils.readText('buy.txt')
	buyDf = dbconnect.readAll("BUY", "DATE", "'"+str(date.today().strftime('%d %b %Y'))+"'")
	temp_list = []
	if buyDf.size > 0:
		for index, row in buyDf.iterrows():
			if index == 0:
				temp_list = [row.ITEM1, row.ITEM2, row.ITEM3, row.ITEM4, row.ITEM5]
	
		userDf = dbconnect.read('user')
		for index, row in userDf.iterrows():
			for item in temp_list:
				currentPrice = getPrice(item)
				if dbconnect.hasItem(item, row['id'], 'BOUGHT_LIST', 'NAME', 'ID'):
					continue
				elif checkCondition(item, row['id']) == 0:
					buyItem(item, getQty(currentPrice, row['id']), currentPrice, row['id'])
				
			#df  = utils.readExcel("buyWithCondition.xlsx")
			df = dbconnect.readAll("CONDITION_BUY", 'id', row['id'])
			for indexc, rowc in df.iterrows():
				if rowc['STOCK'] not in temp_list:
					dbconnect.delete("CONDITION_BUY", "STOCK", rowc['STOCK'], "ID", row['id'])
					#removeFromCondition(row['Stock'])
			
	print 'buy '+str(temp_list)
	
if __name__ == "__main__":
    main()