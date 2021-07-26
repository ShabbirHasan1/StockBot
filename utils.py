
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
import newsRun
import sys
import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import dbconnect
from nsetools import Nse

def getNSESymbol(stock):
	return dbconnect.readItemWhere('stock', 'nseid', stock)

def loadingBar(count,total,size):
	percent = float(count)/float(total)*100
	print (str(int(count)).rjust(3,'0')+"/"+str(int(total)).rjust(3,'0') + ' [' + '='*int(percent/10)*size + ' '*(10-int(percent/10))*size + ']')

def drawProgressBar(percent, barLen = 20):
	#os.system("notify-run configure -f https://notify.run/hRtUrGQaxEM0l3VR")
	#sys.stdout.write("\r")
    os.system("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    os.system("[ %s ] %.2f%%" % (progress, percent * 100))
    sys.stdout.flush()


def upsert(dic, key):
	if key in dic:
		dic[key] = dic[key] + 1
	else:
		dic[key] = 0
	return dic

def upsertAverage(dic, key, value, count):
	if key in dic:
		dic[key] = (dic[key]*(count-1)+value)/count
	else:
		dic[key] = value
	return dic

def sendSMS(message, itemList):
	SMS = message
	os.system("notify-run configure -f https://notify.run/hRtUrGQaxEM0l3VR")

	#adding the new shares to be bought
	for item in itemList:
		SMS = SMS + getNSESymbol(item) + ','
			
	notify = Notify()
	notify.send(SMS)
	
def sendSMS2(message1, message2):
	os.system("notify-run configure -f https://notify.run/hRtUrGQaxEM0l3VR")
			
	notify = Notify()
	notify.send(message1+ message2)

def saveToFile(itemList, filename):
	with open(filename, 'w') as f:
		for item in itemList:
			print >> f, item

def saveToFileItem(item, filename):
	with open(filename, 'w') as f:
		print >> f, item

def readExcel(filename):
	df = pd.read_excel(filename, sheet_name=0, keep_default_na=False) # can also index sheet by name or fetch all sheets
	stockList = df
	return df


def readText(fileName):
	#f = open(filename, 'r')
	#boughtList = f.readlines()
	#f.close()
	#return str(boughtList)
	lineList = [line.rstrip('\n') for line in open(fileName)]
	return lineList

def deleteContent(fName):
    with open(fName, "w"):
        pass

def inDayRange(time, days):
	today = date.today()
	#date = today.strftime("%d %b %Y")
	date_object = datetime.strptime(time, '%Y-%m-%d').date()
	delta = today - date_object;
	if delta.days > days:
		return 0
	else:
		return 1

def getDays(time, format):
	today = date.today()
	date_object = datetime.strptime(time, format).date()
	delta = today - date_object
	return delta.days
		
#return average of value of the number of days specified
def getAverage(data, days):
	sum = 0.0
	count = 0
	for row in data:
		if inDayRange(row.get('date'), days):
			sum = sum + float(row.get('close'))
			count = count + 1;
	return sum/count
	
#return average of value of the number of days specified
def getAverageNew(data, days):
	sum = 0.0
	for row in data:
		sum = sum + float(row.get('close'))
		
	return sum/days	
	
#defining Q2 (jan-mar) 2020 as the starting point	
def absoluteQuarter(year, period):
	num = (year - 2020)*4
	if period == 'Q1':
		num = num + 1
	if period == 'Q2':
		num = num + 2
	if period == 'Q3':
		num = num + 3
	else:
		num = num + 4
		
	return num
	
	
def getShareName(item):
	return dbconnect.readItemWhere('stock', 'fullname', item)
	#wb = xlrd.open_workbook('stock-unique.xlsx')
	#sheet = wb.sheet_by_index(0)
	
	#for row_num in range(sheet.nrows):
	#	row_value = sheet.row_values(row_num)
	#	if row_value[0] == str(item):
	#		return row_value[1]
			
def monthToNum(month):
	return{
		'January' : 1,
		'February' : 2,
		'March' : 3,
		'April' : 4,
		'May' : 5,
		'June' : 6,
		'July' : 7,
		'August' : 8,
		'September' : 9, 
		'October' : 10,
		'November' : 11,
		'December' : 12
}[month]

def periodToNum(period):
	return{
		'Q1' : 1,
		'Q2' : 2,
		'Q3' : 3,
		'Q4' : 4
}[period]

def send_mail(send_from,send_to,subject,text,files,server,port,username='',password='',isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("Scores.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Scores.xlsx"')
    msg.attach(part)

    #context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
    #SSL connection only working on Python 3+
    smtp = smtplib.SMTP(server, port)
    if isTls:
        smtp.starttls()
    smtp.login(username,password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()
	
def normalizaScore(score, date):
	days = getDays('2019 '+str(date), '%Y %b %d, %H:%M')
	maxDays = 20
	if days < 20:
		maxDays = days
	return score - (score*maxDays/20.0)

def getAlertScore(stock):
	return 0.0
	# url = 'https://www.moneycontrol.com/news18/stocks/overview/'+str(stock)+'/N'
	# headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}

	# rcomp = requests.get(url, headers=headers)
	# data = json.loads(rcomp.text)
	# scoreNews = 0.0
	# try:
		# items = data['alerts']
		# for row in items: 
			# if str(row.get('title')) == 'News':
				# scoreNews = scoreNews + normalizaScore(newsRun.getNewsScore(str(stock), str(row.get('message'))), str(row.get('entdate')))		
	# except Exception as e:
		# print (e)
	# return scoreNews
	
def getBalance(id):
	#balances = readText('balance.txt')
	#balance = 0.0
	#for item in balances:
	#	balance = item
	#return float(str(balance))
	df = dbconnect.readAll("BALANCE", 'ID', id)
	for index, row in df.iterrows():
		if index == 0:
			print ('returning amount :'+ str(row['AMOUNT']))
			return float(row['AMOUNT'])
			
	return 0.0
	
def getFund(id):
	#balances = readText('balance.txt')
	#balance = 0.0
	#for item in balances:
	#	balance = item
	#return float(str(balance))
	df = dbconnect.readAll("BALANCE", 'ID', id)
	for index, row in df.iterrows():
		if index == 0:
			print ('returning amount :'+ str(row['FUND']))
			return float(row['FUND'])
			
	return 0.0
	
def hasItem(text, file, column):
	df  = readExcel(file)
	for index, row in df.iterrows():
		if str(row[column]) == text:
			return True
	return False
	
def getZerodhaPrice(price, qty, type):
	CTT = price*qty*0.001
	trans = price*qty*0.0000325
	GST = 0.18*(CTT+trans)
	if type == "B":
		return price + (CTT+trans+GST)/qty
	else:
		return price - (CTT+trans+GST)/qty
	
def checkQuantity(symbol, type):
	url = 'https://www.moneycontrol.com/news18/stocks/overview/'+str(symbol)+'/N'
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}

	rcomp = requests.get(url, headers=headers)
	data = json.loads(rcomp.text)
	
	if type == "B":
		qty = data['NSE']['offerqty']
	if type == "S":
		qty = data['NSE']['bidqty']
	
	print ('Qty: '+str(qty)+' for '+symbol)
	if float(qty) == 0:
		return False
	else:
		return True
		
def checkcircuit(symbol, type):
	url = 'https://www.moneycontrol.com/news18/stocks/overview/'+str(symbol)+'/N'
	headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}

	rcomp = requests.get(url, headers=headers)
	data = json.loads(rcomp.text)
	
	if type == "B":
		if float(data['NSE']['lcprice']) == float(float(data['NSE']['offerprice'])):
			return False
		else:
			return True
	if type == "S":
		if float(data['NSE']['ucprice']) == float(float(data['NSE']['bidprice'])):
			return False
		else:
			return True
			
#scenarios where Q1 result is dated in dec
def getActualYear(date,period):
	#print(date)
	year = date[0:4]
	monthNum = date[5:7]
	#print(monthNum)
	if int(monthNum) > 9 and period == 'Q1':
		return str(int(year)+1)
	
	if int(monthNum) < 6 and period == 'Q4':
		return str(int(year)-1)
		
	if int(monthNum) < 3 and period == 'Q2':
		return str(int(year)-1)
	
	if int(monthNum) < 6 and period == 'Q3':
		return str(int(year)-1)
	
	return str(year)