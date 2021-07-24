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
#from notify_run import Notify
import os
import xlrd
#import xlsxwriter
#import utils
#from openpyxl import load_workbook
#import dbconnect
import dbconnect_new
import dbconnect3
import dbconnect4

def main():
	#main function
	print ('Running median')
	
	#read list of all stock
	ratioList = ['netProfitMarginTTM','returnOnCapitalEmployedTTM','returnOnAssetsTTM','returnOnEquityTTM', 'debtEquityRatioTTM','priceEarningsRatioTTM','dividendYieldTTM']
	count = 0
	
	#df = utils.readExcel('Ratios.xlsx')
	df1 = dbconnect3.read('Ratios')
	df2 = dbconnect4.read('Ratios')

	#frames = [df1, df2]
	df = pd.concat([df1, df2])

	#df = dbconnect.read("`TABLE 2`")
	
	# Replace the column with the converted values
	df['netProfitMarginTTM'] = pd.to_numeric(df['netProfitMarginTTM'], errors='coerce')
	df['returnOnCapitalEmployedTTM'] = pd.to_numeric(df['returnOnCapitalEmployedTTM'], errors='coerce')
	df['returnOnAssetsTTM'] = pd.to_numeric(df['returnOnAssetsTTM'], errors='coerce')
	df['returnOnEquityTTM'] = pd.to_numeric(df['returnOnEquityTTM'], errors='coerce')
	df['debtEquityRatioTTM'] = pd.to_numeric(df['debtEquityRatioTTM'], errors='coerce')
	df['priceEarningsRatioTTM'] = pd.to_numeric(df['priceEarningsRatioTTM'], errors='coerce')
	df['dividendYieldTTM'] = pd.to_numeric(df['dividendYieldTTM'], errors='coerce')
	
	
	for item in ratioList:
		try:
			# Drop NA values, listing the converted columns explicitly
			#   so NA values in other columns aren't dropped
			df.dropna(subset = ['netProfitMarginTTM','returnOnCapitalEmployedTTM','returnOnAssetsTTM','returnOnEquityTTM', 'debtEquityRatioTTM','priceEarningsRatioTTM','dividendYieldTTM'])
			df2 = df.groupby(['industry', 'date', 'period'], as_index=False)[item].median()
			dbconnect_new.upsertDF((str(item).replace('/','-')).lower(), df2)
			
			#change this
			#df2.to_excel(str(item).replace('/','-')+'.xlsx', sheet_name=str(count))
			print (item + " done")
			count = count + 1
		except Exception as e:
			print (e) 

if __name__ == "__main__":
    main()
	
