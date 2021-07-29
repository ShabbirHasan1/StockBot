from futu import *
trd_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSG)
ret, data = trd_ctx.accinfo_query()
if ret == RET_OK:
    print(data)
    print(data['power'][0])  # Get the first buying power
    print(data['power'].values.tolist())  # convert to list
else:
    print('accinfo_query error: ', data)
trd_ctx.close()  # Close the current connection
