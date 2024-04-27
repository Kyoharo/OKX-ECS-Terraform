from dotenv import load_dotenv
import os
from actions.get import DataReader
from actions.get import OKXAPI
from actions.post import DataAction

class CryptoTrader:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.secret_key = os.getenv("SECRET_KEY")
        self.passphrase = os.getenv("PASSPHRASE")
        self.unique_names = os.getenv("UNIQUE_NAMES").split(',')
        self.okx_api = OKXAPI()
        self.coin_to_buy = int(os.getenv("COIN_TO_BUY", 10))  # Default to 10 if not specified

    def calculate_buy_amount(self, available_balance, usdt_balance):
        if len(available_balance) <= self.coin_to_buy:
            return float(usdt_balance) / (self.coin_to_buy - len(available_balance) + 1)
        else:
            return float(usdt_balance)  # Default to using all USDT balance

    def trade(self):
        self.buy_new_crypto()
        self.sell_crypto()

    def buy_new_crypto(self):
        position_summary_data = self.okx_api.fetch_position_summary(self.unique_names)
        if position_summary_data:
            for item in position_summary_data:
                new_crypto = item["instId"]
                print(item['posSide'])
                if new_crypto:
                    data_reader = DataReader(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                    available_balance = data_reader.get_account_balance()
                    usdt_available = False
                    usdt_balance = 0  # Define outside loop
                    for balance_item in available_balance:
                        if balance_item['ccy'] == 'USDT' and float(balance_item['eqUsd']) > 10:
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
                            buy_crypto = DataAction(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                            buy_amount = self.calculate_buy_amount(available_balance, usdt_balance)
                            usdt_balance_formatted = str(int(float(buy_amount)))
                            buy_crypto.post_order(new_crypto.replace("-SWAP", ""), "buy", "market", usdt_balance_formatted)
                            trader = item["uniqueName"]
                            print(f"Trader: {trader}\n>> {new_crypto}: has been bought successful")
                    else:
                        print(f"{new_crypto} :Not enough USDT available")
                else:
                    print("No new crypto found")
        else:
            # print("No position summary data found")
            pass

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
                        if f"{ccy}-USDT-SWAP" == new_crypto or f"BTC-USDT-SWAP" == new_crypto or f"ETH-USDT-SWAP" == new_crypto:
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
            pass
            #print("No position history data found")
