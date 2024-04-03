import okx.Account as Account
import okx.Trade as Trade
from dotenv import load_dotenv
import os
load_dotenv()



flag = "0"  # live trading: 0, demo trading: 1
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
passphrase = os.getenv("PASSPHRASE")

class DataAction:
    def __init__(self, api_key, secret_key, passphrase, live_trading=True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.live_trading = live_trading
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)

    def post_order(self,crypto,order_action,order_type,quantity,price=None):
        result = self.tradeAPI.place_order(
            instId=crypto,
            tdMode="cash",
            side= order_action, #buy or sell
            posSide="net",
            ordType= order_type,    #limit or market
            sz=quantity, #quantity
            px=price #price
        )
        print(result['data'][0]['sMsg'])
        if result['code'] == "0":
            status = result['data'][0]['sMsg']
            return status
        elif len(result['data']) > 1:  # Check if there are enough items in the list
            status = result['data'][1]['sMsg']
            return status
        else:
            # Handle the case where there are not enough items in the list
            return "Error: No message available"

        
# buy_crypto = DataAction(api_key, secret_key, passphrase, live_trading=False)
# buy_crypto.post_order(f"BTC-USDT", "sell", "market",'0.00158234789','103.69')
