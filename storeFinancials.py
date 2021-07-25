
from pprint import pprint
import numpy
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
import xlsxwriter
import utils
import dbconnect
import dbconnect5
from openpyxl import load_workbook
import time
import utils
from mysql.connector import errorcode


try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json

def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read()
    return json.loads(data)

def main():
	print ('Storing ratios')
	
	try:
		df = dbconnect.read('stock')
	except Exception as e:
		time.sleep(3700)
		df = dbconnect.read('stock')
	
	#wb = load_workbook("Ratios.xlsx")
	wbHeaders = ['symbol', 'Industry', 'date', 'period', 'price', 'revenue','netIncome','revenueGrowth','netIncomeGrowth', 'eps','epsgrowth']
	
	for num, row in df.iterrows():

		#print 'entering 1'
		try:
			url = ("https://financialmodelingprep.com/api/v3/income-statement/"+str(row['symbol'])+"?apikey=5d8baa00babcbd4081944f3ea6b14c71&period=quarter")
			incomeData = get_jsonparsed_data(url)
			
			
			for item in incomeData:
				#print(item)
				row_data = ["--"] * 7
				row_data[0] = str(row['symbol'])
				row_data[1] = str(row['industry'])
				row_data[2] = utils.getActualYear(str(item['date']), str(item['period']))
				row_data[3] = str(item['period'])
				#row_data[4] = str(row['price'])
				row_data[4] = str(item['revenue'])
				row_data[5] = str(item['netIncome'])
				#row_data[7] = str(item['revenueGrowth'])
				#row_data[8] = str(item['netIncomeGrowth'])
				row_data[6] = str(item['eps'])
				#row_data[10] = str(item['epsgrowth'])
				
				if int(row_data[2]) < 2020:
					continue
			
				# Append Row Values
				try:
					dbconnect5.insertsingle("`income`", row_data)
					time.sleep(3)
				except Exception as e:
					if e.errno == 1062:
						continue
					else:
						print (e)
						time.sleep(3700)
						dbconnect5.insertsingle("`income`", row_data)
				#ws.append(row_data)
		except Exception as e:
			print (e)
		
		try:
			url = ("https://financialmodelingprep.com/api/v3/financial-growth/"+str(row['symbol'])+"?apikey=5d8baa00babcbd4081944f3ea6b14c71&period=quarter")
			incomeData = get_jsonparsed_data(url)
			
			
			for item in incomeData:
				#print(item)
				row_data = ["--"] * 7
				row_data[0] = str(row['symbol'])
				row_data[1] = str(row['industry'])
				row_data[2] = utils.getActualYear(str(item['date']), str(item['period']))
				row_data[3] = str(item['period'])
				#row_data[4] = str(row['price'])
				#row_data[4] = str(item['revenue'])
				#row_data[5] = str(item['netIncome'])
				row_data[4] = str(item['revenueGrowth'])
				row_data[5] = str(item['netIncomeGrowth'])
				#row_data[6] = str(item['eps'])
				row_data[6] = str(item['epsgrowth'])
				
				if int(row_data[2]) < 2020:
					continue
			
				# Append Row Values
				try:
					dbconnect5.insertsingle("`incomegrowth`", row_data)
					time.sleep(3)
				except Exception as e:
					if e.errno == 1062:
						continue
					else:
						print (e)
						time.sleep(3700)
						dbconnect5.insertsingle("`incomegrowth`", row_data)
				#ws.append(row_data)
		except Exception as e:
			print (e)

		#wb.save("Financials.xlsx")
		
if __name__ == "__main__":
    main()
	