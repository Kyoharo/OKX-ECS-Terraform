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
        url = "https://www.okx.com/priapi/v5/ecotrade/public/position-summary"
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
                    if time_diff < 3:  
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
                        parsed_data.append(parsed_item)
            else:
                print("Error:", response.status_code)
                print("Response content:", response.content)  # Print response content for debugging
        return parsed_data

    def fetch_position_history(self, unique_names):
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
                    open_time = datetime.datetime.fromtimestamp(int(item.get("uTime")) / 1000)  # Convert milliseconds to seconds
                    time_diff = (current_time - open_time).total_seconds() / 60  # Convert to minutes
                    # print(f"current_time:{current_time}  ::  open_time:{open_time}")
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
                            "uniqueName":unique_name,
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
                print("Error:", response.status_code)
                print("Response content:", response.content)  # Print response content for debugging

        return parsed_data

        
# unique_names = ['E7C4B5ED74DF4762','C3AAF1F0071C1DB1','2F775E6260F9DA41','2BE980C9BEA40361','823664FB73B79E41','D62E705043000216','5F2E39B8F0FC6F6A','3D97539465A42032','F302816A920BC50D','A426DA00959F951D','D5E7A8430A35CA84','285A1F51A357C8EC','971FBE22F1E97E7A','182685C1CB038116','700EDC6C6F2EB5B0','127BE725D7F66EED','87CE370F79220167','DDF529A6117DBB92','C343256953163322','C3579137DB709CDB','A24E06C746B022B4','BDA9974EA3429B2D','7AC3E000C300234A','94FC2CF4A047C10E','5EAE0133C50F4261','704388CC53DBDA21','7B066CDD82FF181B','5EBC7A151ABB8034','BFAA2A3003D999A2','3C0A650E43C9F05F','70923A619CCB8F2F','BF05EB0167329BD2','07B8F868A4ED90F2','43B321994B98152D','7A26AF50E89FAF5E','59A6D745D6F58B0C','664BD292A54718C3','9B28742D954561AE','2255AC08798746CA','E7FB79AE8F77F63F','84F98ADC6CE3DE19','7F2323E7F25F4D68','00525FDB96915DFC','2BBAE0BFCF0F5B34','3AF59A7A336C421F','1204F4B818CFE3B0','924E8F5A21124498']





# data_reader = DataReader(api_key, secret_key, passphrase, live_trading=False)
# available_balance = data_reader.get_account_balance()
# # Print filtered coins
# for coin in available_balance:
#     ccy = coin.get("ccy", "")
#     eq_usd = coin.get("eqUsd", "")
#     avail_bal = coin.get("availBal", "")
#     u_time = coin.get("uTime", "")
#     # Print the desired values
#     print(f"Currency: {ccy}, EqUsd: {eq_usd}, Equity: {avail_bal}, UTime: {u_time}")

# avaliable_cash_from_coin = data_reader.get_max_order_cash("GPT-USDT")
# print(avaliable_cash_from_coin)
# print("\n\n")
# avaliable_size_from_coin = data_reader.get_max_avail_size("GPT-USDT")
# print(avaliable_size_from_coin)

