
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

#read list of all stock
ratioFiles = ['Net Profit Margin(%)','Return on Assets Excluding Revaluations', 'Return On Net Worth(%)', 'Return On Capital Employed(%)', 'Total Income - Capital Employed(%)', 'Debt Equity Ratio']
financials = ['Total Income From Operations', 'Net Profit/(Loss) For the Period']
shareRatiodf = utils.readExcel('Ratios.xlsx')
#shareRatiodf = dbconnect.read("`TABLE 2`")
shareFinancialdf = utils.readExcel('Financials.xlsx')
#shareFinancialdf = dbconnect.read("`TABLE 1`")

PATdf = utils.readExcel('Net Profit Margin(%).xlsx')
ROAdf = utils.readExcel('Return on Assets Excluding Revaluations.xlsx')
ROWdf = utils.readExcel('Return On Net Worth(%).xlsx')
ROCAdf =  utils.readExcel('Return On Capital Employed(%).xlsx')
NIdf =  utils.readExcel('Total Income - Capital Employed(%).xlsx')
DIdf = utils.readExcel('Dividend Yield.xlsx')
PEdf = utils.readExcel('PE Ratio.xlsx')
DERatio = utils.readExcel('Debt Equity Ratio.xlsx')
buyList = my_dictionary()
trendMap = my_dictionary()
priceMap = my_dictionary()
topBuyList = {}

TRENDWEIGHT = 0.3
IAVGWEIGHT = 0.05
MEDIANWEIGHT = 0.3
PERATIOWEIGHT = 0.05
NEWSWEIGHT = 0.1
QUARTERWEIGHT = 0.2

counter = 0

def getdfMap(ratio):
	return{
		'Net Profit Margin(%)': PATdf,
		'Return on Assets Excluding Revaluations': ROAdf,
		'Return On Net Worth(%)': ROWdf,
		'Return On Capital Employed(%)': ROCAdf,
		'Total Income / Capital Employed(%)': NIdf,
		'PE Ratio':PEdf,
		'Debt Equity Ratio':DERatio
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


def getGrowthScore(share, financial):
	year = 0
	monthNum = 0
	shareFinancial = 0
	prevShareFinancial=0
	score = 0.0
	for index, row in shareFinancialdf.iterrows():
		if row['Share'] == share:
			if int(row['Year']) > year or ((int(row['Year']) == year) and utils.monthToNum(row['Month']) > monthNum):
				try:
					shareFinancial = float(row[financial])
					year = int(row['Year'])
					month = str(row['Month'])
					monthNum = utils.monthToNum(row['Month'])
					break
				except Exception as e:
					continue
					
	for index, row in shareFinancialdf.iterrows():
		if row['Share'] == share:
			if ((int(row['Year']) == year) and utils.monthToNum(row['Month']) == (monthNum-3)) or ((int(row['Year']) == year -1) and utils.monthToNum(row['Month']) == (monthNum+9)):
				try:
					prevShareFinancial = float(row[financial])
					break
				except Exception as e:
					return 0
				
	return getAdjustedScore(shareFinancial, prevShareFinancial)						

	
	
def getEPS(share, year, monthNum):
	for index, row in shareFinancialdf.iterrows():
		if row['Share'] == share:
			if int(row['Year']) == year and utils.monthToNum(row['Month']) == monthNum:
				try:
					return float(row['Basic EPS'])
				except Exception as e:
					return 0
	return 0
	
def getQuarterScore(share):
	score = 0.0
	for item in financials:
		score = score + getGrowthScore(share, item)
	return score

def getValue(share, industry, ratio):
	year = 0
	monthNum = 0
	shareMedian = 0
	industryMedian = 0
	score = 0.0
	global counter
	for index, row in shareRatiodf.iterrows():
		if row['Share'] == share:
			if int(row['Year']) > year or ((int(row['Year']) == year) and utils.monthToNum(row['Month']) > monthNum):
				try:
					shareMedian = float(row[ratio])
					year = int(row['Year'])
					month = str(row['Month'])
					monthNum = utils.monthToNum(row['Month'])
					counter = counter + 1
				except Exception as e:
					continue
	
	for index, row in getdfMap(ratio).iterrows():
		if (row['Industry'] == industry) and (int(row['Year']) == year) and (row['Month'] == month):
			industryMedian = float(row[ratio])
	
	adjustedScore = getAdjustedScore(shareMedian, industryMedian)		
	
	if ratio=='Debt Equity Ratio':
		adjustedScore = adjustedScore*-1
	return adjustedScore

def getMedianScore(share, industry):
	score = 0.0
	global counter
	counter = 0
	for item in ratioFiles:
		score = score + getValue(share, industry, str(item).replace('-','/'))
	return score/counter
	
def getPEScore(share, currentPrice, industry):
	year = 0
	monthNum = 0
	eps = 0.0
	pe = 0.0
	industryMedian = 0
	score = 0.0
	for index, row in shareRatiodf.iterrows():
		if row['Share'] == share:
			if int(row['Year']) > year or ((int(row['Year']) == year) and utils.monthToNum(row['Month']) > monthNum):	
				try:
					eps = float(row['Earnings Per Share'])
					pe = currentPrice/eps
					year = int(row['Year'])
					month = str(row['Month'])
					monthNum = utils.monthToNum(row['Month'])
				except Exception as e:
					#print e
					continue
				
	for index, row in getdfMap('PE Ratio').iterrows():
		if (row['Industry'] == industry) and (int(row['Year']) == year) and (row['Month'] == month):
			industryMedian = float(row['PE Ratio'])
	
	return -1.0 * getAdjustedScore(pe, industryMedian)
	

def getTrendScore(data):
	try:
		avg200 = utils.getAverage(data['graph']['values'], 200)
		avg50 = utils.getAverage(data['graph']['values'], 50)
		currentPrice = float(data['graph']['current_close'])
		
		return getAdjustedScore(avg50, avg200)
	except Exception as e:
		return 0

def main():
	
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}

	print 'Running stock scoring'
	#read list of all stock
	df = utils.readExcel('stock-unique.xlsx')
	averageList = my_dictionary()
	countList = my_dictionary()
	positiveList = my_dictionary()
	count = 0.0
	#totalStock = 60.0
	totalStock = 2508.0
	wb = load_workbook("Scores.xlsx")
	wbHeaders = ['Share', 'Industry', 'Trend', 'Average', 'Median', 'PE', 'News', 'Quarter', 'Total']
	wb.remove(wb.worksheets[0])
	wb.create_sheet('Scores', 0)
	ws = wb.worksheets[0]

	ws.append(wbHeaders)
	#iterate every stock
	for index, row in df.iterrows():
		try:
			#utils.drawProgressBar(count/totalStock, 50)
			utils.loadingBar(count, totalStock, 10)
			
			count = count + 1
			#runtime calculate change average and percentage of stocks on the rise
			url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+str(row['id'])
			rcomp = requests.get(url, headers=headers)
			data = json.loads(rcomp.text)
			trendScore = getTrendScore(data) * TRENDWEIGHT * 2
			trendMap.add(str(row['id']), trendScore)
			priceMap.add(str(row['id']), float(data['graph']['current_close']))
			#stockData.add(str(row['id']), data)
			currentPrice = float(data['graph']['current_close'])
			prevPrice = float(data['graph']['prev_close'])
			change  = currentPrice/prevPrice
			countList = utils.upsert(countList, str(row['Industry']))
			averageList = utils.upsertAverage(averageList, str(row['Industry']), change, countList[str(row['Industry'])])
			if currentPrice > prevPrice:
				positiveList = utils.upsertAverage(positiveList, str(row['Industry']), 1, countList[str(row['Industry'])])
			else:
				positiveList = utils.upsertAverage(positiveList, str(row['Industry']), 0, countList[str(row['Industry'])])
			
			
		except Exception as e:
			print str(e)+' '+str(row['id'])
			
		
	#iterate every stock
	for index, row in df.iterrows():
		try:
			#utils.drawProgressBar(count/totalStock, 50)
			utils.loadingBar(count, totalStock, 10)
			count = count + 1
			currentPrice = priceMap[str(row['id'])]
			row_data = [None] * 9
			row_data[0] = str(row['id'])
			row_data[1] = str(row['Industry'])
			
			#give trend score
			trendScore = trendMap[str(row['id'])]
			row_data[2] = str(trendScore)
			
			#give industry change score
			industryScore = getAdjustedScore(averageList[str(row['Industry'])], 1.0) * IAVGWEIGHT * 10
			row_data[3] = str(industryScore)
	
			#give ratio median score
			medianScore = getMedianScore(str(row['id']), str(row['Industry'])) * MEDIANWEIGHT
			row_data[4] = str(medianScore)
	
			quarterScore = getQuarterScore(str(row['id']))*QUARTERWEIGHT
			row_data[7] = str(quarterScore)
			
			peScore = getPEScore(str(row['id']), currentPrice, str(row['Industry']))*PERATIOWEIGHT
			row_data[5] = str(peScore)
			
			newsScore = utils.getAlertScore(str(row['id'])) * NEWSWEIGHT
			row_data[6] = str(newsScore)
			
			total = trendScore + industryScore + medianScore + peScore + newsScore + quarterScore
			row_data[8] = str(total)
			ws.append(row_data)
			#print 'Trendscore: '+str(trendScore)+ '| Industry score: '+str(industryScore)+'| Median Score '+str(medianScore)+ '|PE Score '+str(peScore)+'|News Score '+str(newsScore)+'|Quarter score '+str(quarterScore)+'| Total '+str(total) 
			
			buyList.add(str(row['id']), total)
		except Exception as e:
			print e
			continue
	
	#find top buy list
	topBuyList = dict(Counter(buyList).most_common(5))
	utils.saveToFile(topBuyList, 'buy.txt')
	wb.save("Scores.xlsx")
	print 'Top shares to be bought are:'
	print topBuyList
	
	utils.sendSMS('buy ', topBuyList)
	try:
		utils.send_mail('sukrit.raghuvanshi1990@gmail.com','sukrit.raghuvanshi1990@gmail.com','Scores','PFA','Scores.xlsx','smtp.gmail.com',587,'sukrit.raghuvanshi1990','Crashing@1',True)
	except Exception as e:
		print e

if __name__ == "__main__":
    main()
            