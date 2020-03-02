import order
import generate_token
import kiteconnect

def main():
	try:
		print order.getHoldings()
	except kiteconnect.exceptions.TokenException as e:
		generate_token.main()
		

if __name__ == "__main__":
    main()