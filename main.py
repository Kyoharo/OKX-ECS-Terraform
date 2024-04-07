from dotenv import load_dotenv
import os
from OKX_by_Me.get import DataReader
from OKX_by_Me.get import OKXAPI
from OKX_by_Me.post import DataAction
from time import sleep
load_dotenv()


flag = "0"  # live trading: 0, demo trading: 1
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
passphrase = os.getenv("PASSPHRASE")

unique_names = ['A8AF8AFFAB6051B3',# Plymouth
                '2255AC08798746CA', #champion🏆 
                'D5E7A8430A35CA84', #Average-Moon-Cypress 
                'DDF529A6117DBB92', #Back-Cap-Octopus 
                'A426DA00959F951D', #viking212
                '7A26AF50E89FAF5E', #Dry-Peg-Jack 
                '43B321994B98152D',#Mr. Zheng 
                'E7C4B5ED74DF4762'#ITEKCrypto
]


while True:
    #position_summary
    okx_api = OKXAPI()
    position_summary_data = okx_api.fetch_position_summary(unique_names)
    if position_summary_data:
        for item in position_summary_data:
            print(item)
            new_crypto = item["instId"]
            if new_crypto: 
                print(f"Fine New crypto {new_crypto}")
                #read current balance 
                data_reader = DataReader(api_key, secret_key, passphrase, live_trading=False)
                available_balance = data_reader.get_account_balance()
                #check if i have more then 40 USDT
                usdt_available = False
                for balance_item in available_balance:
                    if balance_item['ccy'] == 'USDT' and float(balance_item['eqUsd']) > 40:
                        usdt_available = True
                        usdt_balance = balance_item['eqUsd']
                        
                        break
                
                if usdt_available == True:
                    already_exist = False
                    for balance_item in available_balance:
                        ccy = balance_item['ccy']
                        if f"{ccy}-USDT-SWAP" == new_crypto:
                            print(f"{new_crypto} matches with {ccy}-USDT-SWAP in available balance.")
                            already_exist = True
                    if already_exist == False:
                        open_avg_px = float(item.get("openAvgPx"))
                        last = float(item.get("last"))
                        percentage_difference = abs((last - open_avg_px) / open_avg_px) * 100
                        print(f"percentage_difference= {percentage_difference}")
                        if percentage_difference < 2:
                            #gonna buy the new crypto 
                            buy_crypto = DataAction(api_key, secret_key, passphrase, live_trading=False)
                            if len(available_balance) == 1:
                                print("last stage1")
                                new_crypto = new_crypto.replace("-SWAP", "")
                                buy_amount = float(usdt_balance) / 2  # Convert to float before division
                                usdt_balance_formatted = str(int(float(buy_amount)))
                                buy_crypto.post_order(new_crypto, "buy", "market", usdt_balance_formatted)

                            else:
                                print("last stage")
                                usdt_balance_formatted = str(int(float(usdt_balance)))
                                new_crypto = new_crypto.replace("-SWAP", "")
                                buy_crypto.post_order(new_crypto, "buy", "market",usdt_balance_formatted)
                else:
                    print(F"usdt_available = {usdt_available}")                               

    #------------------------------------------------------------------
    # position_history
    position_summary_data = okx_api.fetch_position_history(unique_names)
    if position_summary_data:
        for item in position_summary_data:
            print(item)
            new_crypto = item["instId"]
            if new_crypto: 
                print(f"Fine sold crypto {new_crypto}")
                #read current balance 
                data_reader = DataReader(api_key, secret_key, passphrase, live_trading=False)
                available_balance = data_reader.get_account_balance()
                already_exist = False
                #check if i have this crypto to sale 
                for balance_item in available_balance:
                    ccy = balance_item['ccy']
                    if f"{ccy}-USDT-SWAP" == new_crypto:
                        print(f"{new_crypto} matches with {ccy}-USDT-SWAP in available balance.")
                        already_exist = True
                    if already_exist == True:
                        #gonna sale the crypto 
                        print("in")
                        sale_crypto = DataAction(api_key, secret_key, passphrase, live_trading=False)
                        sold_crypto = new_crypto.replace("-SWAP", "")
                        #get available cash from crypto coin
                        max_avail_cash = data_reader.get_max_order_cash(sold_crypto) 
                        max_avail_size = data_reader.get_max_avail_size(sold_crypto)
                        sale_crypto.post_order(sold_crypto, "sell", "market",max_avail_size[1], max_avail_cash[1])
                    else:
                        print("I don't have the crypto coin to sell")

    print("waiting 15 sc")
    sleep(30)