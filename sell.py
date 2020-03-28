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
import os
import xlrd
import order
import utils
import dbconnect
from openpyxl import load_workbook


def getAnnualReturn(currentPrice, purchasePrice, purchaseDate):
	ROI  = currentPrice*.995/purchasePrice
	today = date.today()
	delta = today - purchaseDate;
	deltaPer = float(delta.days + 1)/365.0
	return pow(ROI,1/deltaPer)

def getReturn(currentPrice, purchasePrice):
	#removing broker charges
	ROI  = currentPrice*.9943/purchasePrice*1.0057
	return ROI

def shouldSell(currentPrice, purchasePrice, purchaseDate, quantity):
	#sell if annual return is more than 105%
	if getReturn(currentPrice, purchasePrice) > 1.05:
		return 1
	
	return 0
	
def sellAll(item, price, qty, id):
	df  = dbconnect.read("BOUGHT_LIST")
	
	#read balance from file
	balance = utils.getBalance(id)
	
	row_data = [None] * 2
	
	status = order.place_order(item, "S", qty, id)
	if status==1:
		print 'Sell Item :'+item+' | Qty :'+ str(qty)+' | Sell :'+str(price)
		newBalance = float(balance) + (price*qty)
		#utils.saveToFileItem(str(newBalance), 'balance.txt')
		dbconnect.upsert("BALANCE", (id, str(newBalance)) )
		buyDf = dbconnect.read("BUY")
		temp_list = []
		for index, row in buyDf.iterrows():
			if index == 0:
				temp_list = [row.ITEM1, row.ITEM2, row.ITEM3, row.ITEM4, row.ITEM5]
			if item in temp_list:
				#wb = load_workbook("buyWithCondition.xlsx")
				#ws = wb.worksheets[0]
				row_data = [None] * 3
				row_data[0] = id
				row_data[1] = str(item)
				row_data[2] = str(price*.975)
				dbconnect.upsert('CONDITION_BUY', row_data)
				
		dbconnect.delete('BOUGHT_LIST', 'NAME', item, "ID", id)
	
def main():
	#main function
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}
	print "Running seller"
	#df = utils.readExcel('boughtList.xlsx')
	userDf = dbconnect.read('user')
	for index, row in userDf.iterrows():
		sellList = []
		df = dbconnect.readAll('BOUGHT_LIST', 'id', row['id'])
		for index, row in df.iterrows():
			print 'Running for '+ str(row['NAME'])
			url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+str(row['NAME'])
			rcomp = requests.get(url, headers=headers)
			data = json.loads(rcomp.text)
			currentPrice = float(data['graph']['current_close'])
			if shouldSell(currentPrice, float(row['PRICE']), datetime.strptime(row['DATE'], '%d %b %Y').date(), int(row['QTY'])):
				sellList.append(row['NAME'])
				sellAll(str(row['NAME']), currentPrice, int(row['QTY']), row['id'])
			
	#if len(sellList) is not 0:
	#	utils.sendSMS('sell ', sellList)
	
	print 'sell '+str(sellList)
	
if __name__ == "__main__":
    main()
