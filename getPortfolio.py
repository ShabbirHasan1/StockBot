from flask import Flask, json
from flask import jsonify, request
import dbconnect
import requests

api = Flask(__name__)

@api.route('/portfolio', methods=['GET'])
def get_portfolio():
	try:
		id = request.args.get('id')
		headers = {'authorization': "Basic API Key Ommitted", 'accept': "application/json", 'accept': "text/csv"}
		if id:
			df = dbconnect.readAll('BOUGHT_LIST', 'ID', id)
			value = 0.0
			for index, row in df.iterrows():
				url = 'https://appfeeds.moneycontrol.com//jsonapi//stocks//graph&format=json&range=max&type=area&ex=&sc_id='+str(row['NAME'])
				rcomp = requests.get(url, headers=headers)
				data = json.loads(rcomp.text)
				currentPrice = float(data['graph']['current_close'])
				value = value + (currentPrice * float(row['QTY']))
			value = value+float(dbconnect.readItem('BALANCE', 'FUND', 'ID', id))
			initial = float(dbconnect.readItem('BALANCE', 'INITIAL', 'ID', id))
			dict = {}
			dict['Invested'] = initial
			dict['Current'] = value
			dict['Return'] = (value - initial)/initial
			
			return json.dumps(dict)
		else:
			resp = jsonify('User "id" not found in query string')
			resp.status_code = 500
			return resp
	except Exception as e:
		print(e)
  

if __name__ == '__main__':
    api.run(host='0.0.0.0')