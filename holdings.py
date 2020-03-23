#!/usr/bin/python2.7
import generate_token
import kiteconnect
import order

def main():
	try:
		print order.getHoldings()
	except kiteconnect.exceptions.TokenException as e:
		generate_token.main()
	except kiteconnect.exceptions.PermissionException as e:
		generate_token.main()
		
if __name__ == "__main__":
    main()