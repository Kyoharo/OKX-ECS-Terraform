from dotenv import load_dotenv
import os
from get import DataReader
from get import OKXAPI
from post import DataAction

class CryptoTrader:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.secret_key = os.getenv("SECRET_KEY")
        self.passphrase = os.getenv("PASSPHRASE")
        self.unique_names = os.getenv("UNIQUE_NAMES").split(',')
        self.okx_api = OKXAPI()

    def trade(self):
        self.buy_new_crypto()
        self.sell_crypto()

    def buy_new_crypto(self):
        position_summary_data = self.okx_api.fetch_position_summary(self.unique_names)
        if position_summary_data:
            for item in position_summary_data:
                new_crypto = item["instId"]
                if new_crypto:
                    data_reader = DataReader(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                    available_balance = data_reader.get_account_balance()
                    usdt_available = False
                    for balance_item in available_balance:
                        if balance_item['ccy'] == 'USDT' and float(balance_item['eqUsd']) > 30:
                            usdt_available = True
                            usdt_balance = balance_item['eqUsd']
                            break
                    if usdt_available:
                        already_exist = False
                        for balance_item in available_balance:
                            ccy = balance_item['ccy']
                            if f"{ccy}-USDT-SWAP" == new_crypto:
                                already_exist = True
                                break
                        if not already_exist:
                            open_avg_px = float(item.get("openAvgPx"))
                            last = float(item.get("last"))
                            percentage_difference = abs((last - open_avg_px) / open_avg_px) * 100
                            if percentage_difference < 2:
                                buy_crypto = DataAction(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                                if len(available_balance) == 1:
                                    new_crypto = new_crypto.replace("-SWAP", "")
                                    buy_amount = float(usdt_balance) / 2
                                    usdt_balance_formatted = str(int(float(buy_amount)))
                                    buy_crypto.post_order(new_crypto, "buy", "market", usdt_balance_formatted)
                                    trader = item["uniqueName"]
                                    print(f"Trader: {trader}\n>> {new_crypto}: has been bought successful")
                                else:
                                    usdt_balance_formatted = str(int(float(usdt_balance)))
                                    new_crypto = new_crypto.replace("-SWAP", "")
                                    buy_crypto.post_order(new_crypto, "buy", "market",usdt_balance_formatted)
                                    trader = item["uniqueName"]
                                    print(f"Trader: {trader}\n>> {new_crypto}: has been bought successful")


                    else:
                        print("Not enough USDT available")
                else:
                    print("No new crypto found")
        else:
            print("No position summary data found")

    def sell_crypto(self):
        position_history_data = self.okx_api.fetch_position_history(self.unique_names)
        if position_history_data:
            for item in position_history_data:
                new_crypto = item["instId"]
                if new_crypto:
                    data_reader = DataReader(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                    available_balance = data_reader.get_account_balance()
                    already_exist = False
                    for balance_item in available_balance:
                        ccy = balance_item['ccy']
                        if f"{ccy}-USDT-SWAP" == new_crypto:
                            already_exist = True
                            break
                    if already_exist:
                        sale_crypto = DataAction(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                        sold_crypto = new_crypto.replace("-SWAP", "")
                        max_avail_cash = data_reader.get_max_order_cash(sold_crypto)
                        max_avail_size = data_reader.get_max_avail_size(sold_crypto)
                        sale_crypto.post_order(sold_crypto, "sell", "market", max_avail_size[1], max_avail_cash[1])
                        trader = item["uniqueName"]
                        print(f"Trader: {trader}\n>> {new_crypto}: has been sold successful")
                    else:
                        trader = item["uniqueName"]
                        print(f"Trader: {trader}\n>> {new_crypto}: I don't have the crypto coin to sell")
        else:
            print("No position history data found")