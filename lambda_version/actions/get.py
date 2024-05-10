import okx.Account as Account
from dotenv import load_dotenv
import time
import datetime
import requests
import os
load_dotenv()



flag = "0"  # live trading: 0, demo trading: 1
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
passphrase = os.getenv("PASSPHRASE")

class DataReader:
    def __init__(self, api_key, secret_key, passphrase, live_trading=True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.live_trading = live_trading
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

    def get_account_balance(self):
        result = self.accountAPI.get_account_balance()
        data = result.get('data', [])
        filtered_coins = [coin for coin_data in data for coin in coin_data.get('details', []) if 'eqUsd' in coin and float(coin['eqUsd']) > 1]
        return filtered_coins
    
    def get_max_order_cash(self, crypto_name): #return how much cash u have from the the coin 

        result = self.accountAPI.get_max_order_size(
            instId=crypto_name,
            tdMode="cash"
        )
        if result['code'] == "0":
            maxBuy = result['data'][0]['maxBuy']
            maxSell = result['data'][0]['maxSell']
            return maxBuy,maxSell
        else:
            return None

    def get_max_avail_size(self, crypto_name): #return how many u can buy or sell 

        result = self.accountAPI.get_max_avail_size(
            instId=crypto_name,
            tdMode="cash"
        )
        if result['code'] == "0":
            maxBuy = result['data'][0]['availBuy']
            maxSell = result['data'][0]['availSell']
            return maxBuy,maxSell
        else:
            return None
        

#scraping 
class OKXAPI:
    def __init__(self):
        pass

    def fetch_position_summary(self, unique_names):
        try:
            url = "https://www.okx.com/priapi/v5/ecotrade/public/position-detail"
            current_time = datetime.datetime.now()
            parsed_data = []
            encountered_cryptos = set()
            crypto_count = {}

            for unique_name in unique_names:
                timestamp = str(int(time.time() * 1000))  
                params = {
                    "instType": "SWAP",
                    "uniqueName": unique_name,
                    "t": timestamp  # Use the generated timestamp value
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data['data']:
                        open_time = datetime.datetime.fromtimestamp(int(item.get("openTime")) / 1000)  # Convert milliseconds to seconds
                        time_diff = (current_time - open_time).total_seconds() / 60  # Convert to minutes
                        if time_diff < 2:  
                            crypto = item.get("instId")
                            mark_px = "{:.3f}".format(float(item.get("markPx")))
                            open_avg_px = "{:.3f}".format(float(item.get("openAvgPx")))
                            last = "{:.3f}".format(float(item.get("last")))
                            pnl_ratio = "{:.3f}%".format(float(item.get("pnlRatio")) * 100)
                            if crypto not in encountered_cryptos:  # Check if this crypto has been encountered before
                                encountered_cryptos.add(crypto)
                            if crypto not in crypto_count:
                                crypto_count[crypto] = 1
                            else:
                                crypto_count[crypto] += 1
                            parsed_item = {
                                "uniqueName":unique_name,
                                "posSide":item.get("posSide"),
                                "side":item.get("side"),
                                "instId": crypto,
                                "margin": item.get("margin"),
                                "markPx": mark_px,
                                "openAvgPx": open_avg_px,
                                "last":last,
                                "openTime": open_time.strftime('%Y-%m-%d %H:%M:%S'),  # Convert to a formatted string
                                "uTime": item.get("uTime"),
                                "pnlRatio": pnl_ratio,
                                "appearanceCount": crypto_count[crypto]
                            }
                            if parsed_item["posSide"] == "short" or parsed_item["side"] == "sell": 
                                pass
                            else:
                                parsed_data.append(parsed_item)
                else:
                    print("Error:", response.status_code)
                    print("Response content:", response.content)  # Print response content for debugging
            return parsed_data
        except Exception as e:
            print(e)

    def fetch_position_history(self, unique_names):
        try:
            url = "https://www.okx.com/priapi/v5/ecotrade/public/position-history"
            current_time = datetime.datetime.now()
            parsed_data = []
            encountered_cryptos = set()
            crypto_count = {}

            for unique_name in unique_names:
                timestamp = str(int(time.time() * 1000))  
                params = {
                    "instType": "SWAP",
                    "uniqueName": unique_name,
                    "t": timestamp  # Use the generated timestamp value
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data['data']:
                        if item.get("uTime"):  # Check if uTime field is not empty
                            open_time = datetime.datetime.fromtimestamp(int(item.get("uTime")) / 1000)  # Convert milliseconds to seconds
                            time_diff = (current_time - open_time).total_seconds() / 60  # Convert to minutes
                            if time_diff < 2:  # Check if the difference is less than 2 minutes
                                crypto = item.get("instId")
                                closeAvgPx = "{:.3f}".format(float(item.get("closeAvgPx")))
                                open_avg_px = "{:.3f}".format(float(item.get("openAvgPx")))
                                pnl_ratio = "{:.3f}%".format(float(item.get("pnlRatio")) * 100)
                                if crypto not in encountered_cryptos:  # Check if this crypto has been encountered before
                                    encountered_cryptos.add(crypto)
                                if crypto not in crypto_count:
                                    crypto_count[crypto] = 1
                                else:
                                    crypto_count[crypto] += 1
                                parsed_item = {
                                    "uniqueName": unique_name,
                                    "instId": crypto,
                                    "margin": item.get("margin"),
                                    "openAvgPx": open_avg_px,
                                    "closeAvgPx": closeAvgPx,
                                    "openTime": open_time.strftime('%Y-%m-%d %H:%M:%S'),  # Convert to a formatted string
                                    "pnlRatio": pnl_ratio,
                                    "appearanceCount": crypto_count[crypto]
                                }
                                parsed_data.append(parsed_item)
                        else:
                            pass
                            # print(f"{unique_name}: Empty timestamp encountered, skipping...")
                else:
                    print("Error:", response.status_code)
                    print("Response content:", response.content)  # Print response content for debugging

            return parsed_data
        except Exception as e:
            print(e)