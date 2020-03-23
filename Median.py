#!/usr/bin/python2.7
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
import xlsxwriter
import utils
from openpyxl import load_workbook
import dbconnect
import dbconnect_new
import dbconnect3
import dbconnect4

def main():
	#main function
	print 'Running median'
	
	#read list of all stock
	ratioList = ['Net Profit Margin(%)','Return on Assets Excluding Revaluations', 'Return On Net Worth(%)', 'Return On Capital Employed(%)', 'Total Income / Capital Employed(%)', 'Dividend Yield', 'PE Ratio', 'Debt Equity Ratio']
	count = 0
	
	#df = utils.readExcel('Ratios.xlsx')
	df1 = dbconnect3.read('Ratios')
	df2 = dbconnect4.read('Ratios')

	#frames = [df1, df2]
	df = pd.concat([df1, df2])

	#df = dbconnect.read("`TABLE 2`")
	
	# Replace the column with the converted values
	df['PE Ratio'] = pd.to_numeric(df['PE_Ratio'], errors='coerce')
	df['Net Profit Margin(%)'] = pd.to_numeric(df['Net_Profit_Margin'], errors='coerce')
	df['Return On Net Worth(%)'] = pd.to_numeric(df['Return_On_Net_Worth'], errors='coerce')
	df['Return On Capital Employed(%)'] = pd.to_numeric(df['Return_On_Capital_Employed'], errors='coerce')
	df['Total Income / Capital Employed(%)'] = pd.to_numeric(df['Total_Income_Capital_Employed'], errors='coerce')
	df['Dividend Yield'] = pd.to_numeric(df['Dividend_Yield'], errors='coerce')
	df['Return on Assets Excluding Revaluations'] = pd.to_numeric(df['Return_on_Assets_Excluding_Revaluations'], errors='coerce')
	df['Debt Equity Ratio'] = pd.to_numeric(df['Debt_Equity_Ratio'], errors='coerce')
	
	
	for item in ratioList:
		try:
			# Drop NA values, listing the converted columns explicitly
			#   so NA values in other columns aren't dropped
			df.dropna(subset = ['Net Profit Margin(%)', 'Return On Net Worth(%)', 'Return On Capital Employed(%)', 'Total Income / Capital Employed(%)', 'Dividend Yield', 'Return on Assets Excluding Revaluations', 'PE Ratio', 'Debt Equity Ratio'])
			df2 = df.groupby(['Industry', 'Year', 'Month'], as_index=False)[item].median()
			dbconnect_new.upsertDF((str(item).replace('/','-')).lower(), df2)
			
			#change this
			#df2.to_excel(str(item).replace('/','-')+'.xlsx', sheet_name=str(count))
			print item + " done"
			count = count + 1
		except Exception as e:
			print e 

if __name__ == "__main__":
    main()
	
