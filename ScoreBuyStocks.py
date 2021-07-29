
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
from openpyxl import load_workbook
from collections import defaultdict
from time import strptime
import dbconnect
import dbconnect_new
import dbconnect3
import dbconnect4
import dbconnect5
import time
import sys
import threading

#if sys.version_info > (2, 7):
#	import _thread
#else:
#	import thread

#read list of all stock
ratioFiles = ['netProfitMarginTTM','returnOnCapitalEmployedTTM','returnOnAssetsTTM','returnOnEquityTTM', 'debtEquityRatioTTM','priceEarningsRatioTTM','dividendYieldTTM']
ratioColumn = ['netProfitMarginTTM','returnOnCapitalEmployedTTM','returnOnAssetsTTM','returnOnEquityTTM', 'debtEquityRatioTTM','priceEarningsRatioTTM','dividendYieldTTM']
financials = ['revenue', 'netIncome', 'eps']
#shareRatiodf = utils.readExcel('Ratios.xlsx')
shareRatiodf1 = dbconnect3.read('Ratios')
shareRatiodf2 = dbconnect4.read('Ratios')
shareRatiodf = pd.concat([shareRatiodf1, shareRatiodf2])

#shareRatiodf = dbconnect.read("`TABLE 2`")
#shareFinancialdf = utils.readExcel('Financials.xlsx')
shareFinancialdf = dbconnect5.read("`income`")
#print('income')
shareFinancialGrowthdf = dbconnect5.read("`incomegrowth`")
#print('incomegrowth`')

#PATdf = utils.readExcel('Net Profit Margin(%).xlsx')
PATdf = dbconnect_new.read('`netProfitMarginTTM`')
#ROAdf = utils.readExcel('Return on Assets Excluding Revaluations.xlsx')
ROAdf = dbconnect_new.read('`returnOnAssetsTTM`')
#ROWdf = utils.readExcel('Return On Net Worth(%).xlsx')
ROWdf = dbconnect_new.read('`returnOnEquityTTM`')
#ROCAdf =  utils.readExcel('Return On Capital Employed(%).xlsx')
ROCAdf = dbconnect_new.read('`returnOnCapitalEmployedTTM`')
#NIdf =  utils.readExcel('Total Income - Capital Employed(%).xlsx')
#NIdf = dbconnect_new.read('`total income - capital employed(%)`')
#DIdf = utils.readExcel('Dividend Yield.xlsx')
DIdf = dbconnect_new.read('`dividendYieldTTM`')
#PEdf = utils.readExcel('PE Ratio.xlsx')
PEdf = dbconnect_new.read('`priceEarningsRatioTTM`')
#DERatio = utils.readExcel('Debt Equity Ratio.xlsx')
DERatio = dbconnect_new.read('`debtEquityRatioTTM`')
buyList = my_dictionary()
trendMap = my_dictionary()
priceMap = my_dictionary()
topBuyList = {}

TRENDWEIGHT = 0.2
IAVGWEIGHT = 0.05
MEDIANWEIGHT = 0.4
PERATIOWEIGHT = 0.05
NEWSWEIGHT = 0.1
QUARTERWEIGHT = 0.2

counter = 0
threadLock = threading.Lock()
threads = []


threadLimiter = threading.BoundedSemaphore(100)

class myThread (threading.Thread):
	def __init__(self, symbol):
		threading.Thread.__init__(self)
		self.symbol = symbol
		
	def run(self):
		threadLimiter.acquire()
		# Get lock to synchronize threads
		#threadLock.acquire()
		try:
			trendScoring(self.symbol)
		finally:
			threadLimiter.release()
		# Free lock to release next thread
		#threadLock.release()

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


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

def getGrowthMap(financial):
	return{
		'revenue': 'revenueGrowth',
		'netIncome': 'netIncomeGrowth',
		'eps': 'epsgrowth'
}[financial]

def getdfMap(ratio):
	return{
		'netProfitMarginTTM': PATdf,
		'returnOnAssetsTTM': ROAdf,
		'returnOnEquityTTM': ROWdf,
		'returnOnCapitalEmployedTTM': ROCAdf,
		'priceEarningsRatioTTM':PEdf,
		'debtEquityRatioTTM':DERatio,
		'dividendYieldTTM':DIdf
}[ratio]


def getAdjustedScore(score, benchmark):
	if benchmark == 0:
		return 0
	else:
		gain = (score - benchmark)/abs(benchmark)
	
		if gain > 1.0:
			return 1.0
		if gain < -1.0:
			return -1.0
		else:
			return gain


def getDeltaScore(gain):
		if gain > 1.0:
			return 1.0
		if gain < -1.0:
			return -1.0
		else:
			return gain


def getGrowthScore(share, financial):
	year = 0
	monthNum = 0
	shareFinancial = 0
	prevShareFinancial=0
	score = 0.0
	month = 'Q2'
	
	shareGrowthdf = shareFinancialGrowthdf.loc[shareFinancialGrowthdf['symbol'] == share]
	for index, row in shareGrowthdf.iterrows():
		#if row['symbol'] == share:
		if (utils.absoluteQuarter(int(row['date']), str(row['period'])) > utils.absoluteQuarter(year, month)):
			try:
				shareFinancial = float(row[getGrowthMap(financial)])
				year = int(row['date'])
				month = str(row['period'])
				#monthNum = utils.monthToNum(row['period'])
			except Exception as e:
				print(e)
				continue
	
	return getDeltaScore(shareFinancial)						
	
	
def getEPS(share, year, monthNum):
	shareFdf = shareFinancialdf.loc[shareFinancialdf['symbol'] == share]
	for index, row in shareFdf.iterrows():
		if int(row['date']) == year and utils.monthToNum(row['period']) == monthNum:
			try:
				return float(row['eps'])
			except Exception as e:
				return 0
	return 0
	
def getQuarterScore(share):
	score = 0.0
	count = 0
	for item in financials:
		#print('quarter scoring')
		score = score + getGrowthScore(share, item)
		count = count + 1
		
	if count == 0:
		return 0.0
	
	return score/count

def getValue(share, industry, ratio, ratioColumn):
	year = 0
	monthNum = 0
	shareMedian = 0
	industryMedian = 0
	score = 0.0
	month = 'Q2'
	global counter
	
	sharedf = shareRatiodf.loc[shareRatiodf['symbol'] == share]
	for index, row in sharedf.iterrows():
		#if row['symbol'] == share:
		if (utils.absoluteQuarter(int(row['date']), str(row['period'])) > utils.absoluteQuarter(year, month)):
			try:
				shareMedian = float(row[ratioColumn])
				year = int(row['date'])
				month = str(row['period'])
				#monthNum = utils.monthToNum(row['period'])
				counter = counter + 1
			except Exception as e:
				print(e)
				continue
	
	for index, row in getdfMap(ratio).iterrows():
		if (str(row['industry']) == industry) and (int(row['date']) == year) and (row['period'] == month):
			industryMedian = float(row[ratio])
	
	
	#print ('Share median  '+str(shareMedian)+ ' Industry median : ' + str(industryMedian))
	adjustedScore = getAdjustedScore(shareMedian, industryMedian)		
	
	if ratio=='debtEquityRatioTTM':
		adjustedScore = adjustedScore*-1
	
	#print 'returning '+str(adjustedScore)+ ' ratio: ' + str(ratio)
	return adjustedScore

def getMedianScore(share, industry):
	score = 0.0
	global counter
	counter = 0
	for item in ratioFiles:
		score = score + getValue(share, industry, str(item).replace('-','/'), str(item))

	if counter == 0:
		return 0.0
	return score/counter
	
def getPEScore(share, currentPrice, industry):
	year = 0
	monthNum = 0
	eps = 0.0
	pe = 0.0
	industryMedian = 0
	score = 0.0
	month = 'Q2'
	
	
	sharedf = shareRatiodf.loc[shareRatiodf['symbol'] == share]
	for index, row in sharedf.iterrows():
		#if row['symbol'] == share:
		if (utils.absoluteQuarter(int(row['date']), str(row['period'])) > utils.absoluteQuarter(year, month)):
			try:
				shareMedian = float(row['priceEarningsRatioTTM'])
				year = int(row['date'])
				month = str(row['period'])
				#monthNum = utils.monthToNum(row['period'])
			except Exception as e:
				print(e)
				continue
				
	for index, row in getdfMap('priceEarningsRatioTTM').iterrows():
		if (str(row['industry']) == industry) and (int(row['date']) == year) and (row['period'] == month):
			industryMedian = float(row['priceEarningsRatioTTM'])
	
	return -1.0 * getAdjustedScore(pe, industryMedian)
	

def getTrendScore(symbol):
	try:
		#avg200 = utils.getAverage(data['historical'], 200)
		#avg50 = utils.getAverage(data['historical'], 50)
		#currentPrice = float(data['graph']['current_close'])
		
		url = "https://financialmodelingprep.com/api/v3/technical_indicator/daily/"+symbol+"?period=50&type=sma&apikey=5d8baa00babcbd4081944f3ea6b14c71"
		avg50 = float((get_jsonparsed_data(url)[0]).get('sma'))
		url = "https://financialmodelingprep.com/api/v3/technical_indicator/daily/"+symbol+"?period=200&type=sma&apikey=5d8baa00babcbd4081944f3ea6b14c71"
		avg200 = float((get_jsonparsed_data(url)[0]).get('sma'))
		print(symbol + ' '+ str(avg50)+ ' ' + str(avg200))
		
		return getAdjustedScore(avg50, avg200)
	except Exception as e:
		print(e)
		try:
			url = "https://financialmodelingprep.com/api/v3/technical_indicator/daily/"+symbol+"?period=50&type=sma&apikey=5d8baa00babcbd4081944f3ea6b14c71"
			avg50 = float((get_jsonparsed_data(url)[0]).get('sma'))
			url = "https://financialmodelingprep.com/api/v3/technical_indicator/daily/"+symbol+"?period=200&type=sma&apikey=5d8baa00babcbd4081944f3ea6b14c71"
			avg200 = float((get_jsonparsed_data(url)[0]).get('sma'))
			print(symbol + ' '+ str(avg50)+ ' ' + str(avg200))		
			return getAdjustedScore(avg50, avg200)
		except Exception as e:
			print(e)
			return 0
		
def trendScoring(symbol):
	trendScore = getTrendScore(symbol) * TRENDWEIGHT * 2
	threadLock.acquire()
	trendMap.add(symbol, trendScore)
	time.sleep(1)
	threadLock.release()

def main():
	
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}

	print ('Running stock scoring')
	df = dbconnect.readWhere2('stock', 'exchangeShortName', "('NYSE','NASDAQ')")
	
	count = 0.0
	totalStock = len(df)
	
	#iterate every stock
	#for index, row in df.iterrows():
	#	try:
			#utils.drawProgressBar(count/totalStock, 50)
			
			
			
			
			#if count == 5:
			#	break
	#	except Exception as e:
	#		print (str(e)+' '+str(row['symbol']))
			
	
	#for t in threads:
	#	t.join()
	#print ("Exiting Main Thread")
	#time.sleep(30)
	#rows = ["--"]*100
	rows = []
	counter = 0
	#iterate every stock
	for index, row in df.iterrows():
		try:
			#utils.drawProgressBar(count/totalStock, 50)
			utils.loadingBar(count, totalStock, 10)
			count = count + 1
			
			
			#th = myThread(str(row['symbol']))
			#th.start()
			#threads.append(th)
			
			currentPrice = row['price']
			row_data = [None] * 10
			row_data[0] = str(row['symbol'])
			row_data[1] = str(row['industry'].encode('ascii','ignore'))
			
			#give trend score
			trendScore = getTrendScore(str(row['symbol'])) * TRENDWEIGHT * 2
			row_data[2] = str(trendScore)
			#print ('trend score is '+ str(trendScore))
			
			#give industry change score
			#industryScore = getAdjustedScore(averageList[str(row['industry'])], 1.0) * IAVGWEIGHT * 10
			industryScore = 0
			row_data[3] = str(industryScore)
			#print ('industryScore is '+ str(industryScore))
			
			#give ratio median score
			medianScore = getMedianScore(str(row['symbol']), str(row['industry'].encode('ascii','ignore'))) * MEDIANWEIGHT
			row_data[4] = str(medianScore)
			#print ('medianScore is '+ str(medianScore))
	
			quarterScore = getQuarterScore(str(row['symbol']))*QUARTERWEIGHT
			row_data[7] = str(quarterScore)
			#print ('quarterScore is '+ str(quarterScore))
			
			peScore = getPEScore(str(row['symbol']), currentPrice, str(row['industry'].encode('ascii','ignore')))*PERATIOWEIGHT
			row_data[5] = str(peScore)
			#print ('peScore is '+ str(peScore))
			
			newsScore = utils.getAlertScore(str(row['symbol'])) * NEWSWEIGHT
			row_data[6] = str(newsScore)
			#print 'newsScore is '+ str(newsScore)
			
			total = trendScore + industryScore + medianScore + peScore + newsScore + quarterScore
			#if currentPrice <5.0:
			#	total = total - 1.0
			row_data[8] = str(total)
			row_data[9] = str(date.today().strftime('%d %b %Y'))
			#ws.append(row_data)
			try:
				#rows[counter] = row_data
				rows.append(row_data)
				counter = counter + 1
						
				if counter == 100:
					dbconnect_new.upsert_many("Scores", rows)
					counter = 0
					rows = []
				#dbconnect_new.upsert("Scores", row_data)
				#time.sleep(1)
			except Exception as e:
				print (e)
				time.sleep(3700)
				print ('sleeping')
				dbconnect_new.upsert_many("Scores", rows)
				counter = 0
				rows = []
				#dbconnect_new.upsert("Scores", row_data)
			#print ('Trendscore: '+str(trendScore)+ '| Industry score: '+str(industryScore)+'| Median Score '+str(medianScore)+ '|PE Score '+str(peScore)+'|News Score '+str(newsScore)+'|Quarter score '+str(quarterScore)+'| Total '+str(total))
			
			buyList.add(str(row['symbol']), total)
		except Exception as e:
			print (e)
			continue
	
	dbconnect_new.upsert_many("Scores", rows)
	#dbconnect_new.delete("Scores", "`name`", "--")
	#find top buy list
	topBuyList = dict(Counter(buyList).most_common(5))
	#utils.saveToFile(topBuyList, 'buy.txt')
	print (topBuyList)
	
	finalList = []
	count = 0
	
	for item,value in topBuyList.items():
		# if utils.checkQuantity(item, "B") and utils.checkcircuit(item, "B"):
		finalList.append(item)
		count = count + 1
		if count == 5:
			break
	
	print ('Top shares to be bought are:')
	print (finalList)
	
	dbconnect.upsertList("BUY", finalList)
	utils.sendSMS('buy ', finalList)
	
	#try:
	#	utils.send_mail('sukrit.raghuvanshi1990@gmail.com','sukrit.raghuvanshi1990@gmail.com','Scores','PFA','Scores.xlsx','smtp.gmail.com',587,'sukrit.raghuvanshi1990','Crashing@1',True)
	#except Exception as e:
	#	print e

if __name__ == "__main__":
    main()
            
