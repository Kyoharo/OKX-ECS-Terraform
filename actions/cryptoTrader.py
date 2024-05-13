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
        
    def check_and_write_to_file(self, key, value, file_path):
        # Check if the key-value pair already exists in the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip() == f"{key}:{value}":
                    print("Key-value pair already exists in the file.")
                    return
        
        # If the key-value pair doesn't exist, append it to the file
        with open(file_path, 'a') as file:
            modified_key = f"{key}-SWAP"
            file.write(f"{modified_key}:{value}\n")
        print("Key-value pair added to the file.")
        
    def delete_from_file(self, key, value, file_path):
        # Check if the key-value pair exists in the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        with open(file_path, 'w') as file:
            for line in lines:
                if line.strip() == f"{key}:{value}":
                    print("Key-value pair deleted from the file.")
                    return True
                else:
                    file.write(line)

        print("Key-value pair not found in the file.")
        return False

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
                            self.check_and_write_to_file(new_crypto, trader, "status.txt")
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
                        if f"{ccy}-USDT-SWAP" == new_crypto:
                            already_exist = True
                            break
                    
                    if already_exist:
                        trader = item["uniqueName"]
                        sell = self.delete_from_file(new_crypto, trader, "status.txt")
                        if sell:
                            sale_crypto = DataAction(self.api_key, self.secret_key, self.passphrase, live_trading=False)
                            sold_crypto = new_crypto.replace("-SWAP", "")
                            max_avail_cash = data_reader.get_max_order_cash(sold_crypto)
                            max_avail_size = data_reader.get_max_avail_size(sold_crypto)
                            sale_crypto.post_order(sold_crypto, "sell", "market", max_avail_size[1], max_avail_cash[1])
                            print(f"Trader: {trader}\n>> {new_crypto}: has been sold successful")
                        else:
                            print("Anther saller")
                    else:
                        trader = item["uniqueName"]
                        print(f"Trader: {trader}\n>> {new_crypto}: I don't have the crypto coin to sell")
        else:
            pass
            #print("No position history data found")
