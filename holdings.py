#!/usr/bin/python2.7
import generate_token
import kiteconnect
import order

def main():
	try:
		print order.getHoldings('1')
	except kiteconnect.exceptions.TokenException as e:
		generate_token.generate('1', 'VM3521', 'Crashing@1', '670594')
		print order.getHoldings('1')
	except kiteconnect.exceptions.PermissionException as e:
		generate_token.generate('1', 'VM3521', 'Crashing@1', '670594')
		print order.getHoldings('1')
		
if __name__ == "__main__":
    main()