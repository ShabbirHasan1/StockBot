from nsetools import Nse
from pprint import pprint
import numpy as np
import pandas as pd
import csv
import json 
import requests
nse = Nse()
print nse

def write_to_csv(data, file):
	with open(file, 'w') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(('code', 'name'))
		for key, value in data.items():
			writer.writerow([key, value])

def write_to_csv2(file, all_stock_codes):
	with open(file, 'wb') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(('id','shortname','mktcap','lastvalue','change','percentchange','direction','stk_details','volume','url'))
		headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}

		for i in range (0, 79):
			urlcomp = 'http://appfeeds.moneycontrol.com/jsonapi/market/marketmap&format=&type=0&ind_id='+str(i)
			## API Call to retrieve report
			rcomp = requests.get(urlcomp, headers=headers)
			data = json.loads(rcomp.text)
			if len(data) is not 0:
				for row in data['item']:
					writer.writerow([row.get('id'), row.get('shortname'), row.get('mktcap'), row.get('lastvalue'), row.get('change'), row.get('percentchange'), row.get('direction'), row.get('stk_details'), row.get('volume'), row.get('url')])
			

index_codes = nse.get_index_list()
all_stock_codes = nse.get_stock_codes()
#pprint(all_stock_codes)
print "there are "+str(len(all_stock_codes))+ " codes"
print index_codes
#write_to_csv(all_stock_codes, 'data.csv')




	
write_to_csv2('stock.csv', all_stock_codes)



q = nse.get_quote('infy')
#pprint(q)



