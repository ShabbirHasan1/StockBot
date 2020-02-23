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
	
def sellAll(item, price, qty):
	df  = utils.readExcel("boughtList.xlsx")
	
	#read balance from file
	balance = utils.getBalance()
	
	row_data = [None] * 2
	
	status = order.place_order(item, "S", qty)
	if status==1:
		print 'Sell Item :'+item+' | Qty :'+ str(qty)+' | Sell :'+str(price)
		newBalance = float(balance) + (price*qty)
		utils.saveToFileItem(str(newBalance), 'balance.txt')
		if item in utils.readText('buy.txt'):
			#add to buywithcondition
			wb = load_workbook("buyWithCondition.xlsx")
			ws = wb.worksheets[0]
			row_data = [None] * 2
			row_data[0] = item
			row_data[1] = price*.975
			ws.append(row_data)
			wb.save("buyWithCondition.xlsx")
	
	df = df[df['Name'] != item]
	df.to_excel("boughtList.xlsx",sheet_name='Sheet1',index=False)
	
def main():
	#main function
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}
	print "Running seller"
	sellList = []
	df = utils.readExcel('boughtList.xlsx')
	
	for index, row in df.iterrows():
		print 'Running for '+ str(row['Name'])
		url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+str(row['Name'])
		rcomp = requests.get(url, headers=headers)
		data = json.loads(rcomp.text)
		currentPrice = float(data['graph']['current_close'])
		if shouldSell(currentPrice, float(row['Price']), datetime.strptime(row['Date'], '%d %b %Y').date(), int(row['Qty'])):
			sellList.append(row['Name'])
			sellAll(str(row['Name']), currentPrice, int(row['Qty']))
			
	#if len(sellList) is not 0:
	#	utils.sendSMS('sell ', sellList)
	
	print 'sell '+str(sellList)
	
if __name__ == "__main__":
    main()
