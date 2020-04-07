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
import time

def main():
	#main function
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}
	print "Running history"
	#df = utils.readExcel('boughtList.xlsx')
	userDf = dbconnect.read('user')
	for index, row in userDf.iterrows():
		df = dbconnect.readAll('BOUGHT_LIST', 'id', row['id'])
		value = 0.0
		for index2, row2 in df.iterrows():
			print 'Running for '+ str(row2['NAME'])
			url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+str(row2['NAME'])
			rcomp = requests.get(url, headers=headers)
			data = json.loads(rcomp.text)
			currentPrice = float(data['graph']['current_close'])
			value = value + (currentPrice * float(row2['QTY']))
		value = value+float(dbconnect.readItem('BALANCE', 'FUND', 'ID', row['id']))
		time.sleep(2)
		initial = float(dbconnect.readItem('BALANCE', 'INITIAL', 'ID', row['id']))
		today =  str(date.today().strftime('%d %b %Y'))	
		list = [str(row['id']), today, str(round(initial, 2)), str(round(value,2))]
		dbconnect.upsertsingle("HISTORY", list)
	
if __name__ == "__main__":
    main()
