
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
import utils
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
	
def check(string, sub_str): 
    if (string.find(sub_str) == -1): 
        return 0 
    else: 
        return 1

def getSentiment(sign, message):
	sentiment = 0
	if check(message, 'gains')  or (message, 'jumps') or (message, 'rises') or (message, 'widens') or check(message, 'higher')or check(message, 'up'):
		sentiment = 1
	if check(message, 'loses') or check(message, 'narrows') or check(message, 'falls') or check(message, 'lowers') or check(message, 'plunges') or check(message, 'dips') or check(message, 'down'):
		sentiment = -1
	return sentiment*sign

def getSign(message):
	if check(message, 'profit'):
		return 1
	if check(message, 'loss'):
		return -1
	return 0

def getNewsScore(stock, message):
	if check(message, utils.getShareName(stock)) or check(message, stock) or check(message, utils.getShareName(stock).split()[0]):
		return getSentiment(getSign(message), message)
	else:
		return 0


def main():
	df = utils.readExcel('News.xlsx')
	for index, row in df.iterrows():
		try:
			if str(row['News']) == 'News':
				score = getNewsScore(str(row['Stock']), str(row['Message']))
				print (str(row['Stock']) +' | '+ str(row['Message'])+' | '+str(score))
		except Exception as e:
			print (e)

if __name__ == "__main__":
    main()