import logging
from kiteconnect import KiteConnect
from selenium import webdriver
import time
import urlparse
import utils
import os
import dbconnect
logging.basicConfig(level=logging.DEBUG)

def generate(id, usern, passw, pin):
	kite = KiteConnect(api_key="6m485o0cpsicqsw7")


	print kite.login_url()


	chrome_options = webdriver.ChromeOptions()
	chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--no-sandbox")
	driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

	#driver = webdriver.Chrome()

	driver.get("https://kite.trade/connect/login?api_key=6m485o0cpsicqsw7&v=")



	driver.implicitly_wait(10)

	username = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[1]/input')
	password = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[2]/input')

	username.send_keys(usern)
	password.send_keys(passw)

	driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()


	driver.implicitly_wait(10)

	Security1 = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[2]/div/input')

	Security1.send_keys(pin)

	driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()


	#driver.implicitly_wait(10)
	time.sleep(10)

	#https://kite.trade/?status=success&request_token=5RxqyLUXx56OlgDigy7LHJdzmqZ4Fibd&action=login

	#print driver.current_url

	parsed = urlparse.urlparse(driver.current_url)
	token = urlparse.parse_qs(parsed.query)['request_token'][0]

	# Redirect the user to the login url obtained
	# from kite.login_url(), and receive the request_token
	# from the registered redirect url after the login flow.
	# Once you have the request_token, obtain the access_token
	# as follows.



	data = kite.generate_session(token, api_secret="2h2k6kqpio3xyigxtlor49pcx1g6ofoo")
	print 'Saving token '+str(data["access_token"])
	#utils.saveToFileItem(str(data["access_token"]), 'access_token.txt')
	dbconnect.upsert('TOKEN',(id, str(data["access_token"])))
	#kite.set_access_token(data["access_token"])

def main():
	df = dbconnect.readAll('ACCOUNT', 'TYPE', 'LIVE')
	for index, row in df.iterrows():
		generate(row['ID'], row['USERNAME'], row['PASSWORD'], row['PIN'])

if __name__ == "__main__":
    main()
