import hashlib
import hmac
import requests
import os
from dotenv import load_dotenv

import datetime
import time
import os


class GateAPI:
    def __init__(self, ):
        load_dotenv()
        self.api_key = os.getenv("GATE_API_KEY")
        self.api_secret = os.getenv("GATE_SECRET")
        self.host = "https://api.gateio.ws"
        self.prefix = "/api/v4"
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def gen_sign(self, method, url, query_string=None, payload_string=None):
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(self.api_secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': self.api_key, 'Timestamp': str(t), 'SIGN': sign}

    def post_order(self, crypto, order_action, order_type, quantity, price=None):
        try:
            url = '/spot/orders'
            query_param = ''
            body = f'{{"text":"t-abc123","currency_pair":"{crypto}","type":"{order_type}","account":"spot","side":"{order_action}","amount":{quantity},"time_in_force":"ioc"}}'

            sign_headers = self.gen_sign('POST', self.prefix + url, query_param, body)
            self.headers.update(sign_headers)

            result = requests.request('POST', self.host + self.prefix + url, headers=self.headers, data=body)
            response_data = result.json()  # Parse JSON response
            print(response_data)
            return response_data["finish_as"]

        except Exception as e:
            print(e)


    def get_coin(self, coin_name):
        try:
            url = '/spot/accounts'
            query_param = ''
            coin_name = coin_name.replace("_USDT", "")
            sign_headers = self.gen_sign('GET', self.prefix + url, query_param)
            self.headers.update(sign_headers)
            r = requests.request('GET', self.host + self.prefix + url, headers=self.headers)
            response_data = r.json()
            early_currency_data = next((item for item in response_data if item.get('currency') == coin_name), None)
            return early_currency_data["available"]
        except Exception as e:
            print(e)


    def get_order_book(self, coin_name):
        try:
            url = '/spot/order_book'
            query_param = f'currency_pair={coin_name}'
            r = requests.request('GET', self.host + self.prefix + url + "?" + query_param, headers=self.headers)
            response_data = r.json()
            asks = response_data.get('asks', [])  # Get the 'asks' list
            # Extract prices from all asks and find the lowest price
            prices = [float(item[0]) for item in asks]
            lowest_price = min(prices) if prices else 0
            
            return lowest_price
        except Exception as e: 
            print(e)




def check_time():
    now = datetime.datetime.now()
    if now.hour == 17 and now.minute == 14:
        return True
    else:
        return False




def main(buy_with_usdt,coin_name):
    gate_api = GateAPI()
    buy_with_usdt = buy_with_usdt
    coin_name= coin_name
    while True:
        if check_time():
            print("IN")
            try:
                # Place your order
                results = gate_api.post_order(coin_name, "buy", "market", buy_with_usdt)
                print(results)
                # Check if the response contains the required keys
                if results == "filled":
                    os.system("echo 'Task executed'")  # Print 'Task executed' to the console
                    break
                else:
                    print("Response does not contain expected data.")
            except Exception as e:
                print(e)
                break

    #available quqntity 
    available_quantity_str = gate_api.get_coin(coin_name) 
    available_quantity = float(available_quantity_str) if available_quantity_str else 0.0  # Convert to float, default to 0.0 if string is empty
    #convert the buy with usdt
    buy_with_usdt = float(buy_with_usdt) 
    # Calculate the price at buy 
    price_at_buy = buy_with_usdt / available_quantity if available_quantity != 0 else 0  
    print("Price at buy:", price_at_buy)
    # 1% higher than the price at buy
    threshold_price = price_at_buy + (price_at_buy * 0.01)

    while True:
        order_book_data = gate_api.get_order_book(coin_name)
        print("Market price:", order_book_data)

        if order_book_data > threshold_price:
            print("Market price is at least 1% higher than price at buy. Selling now...")
            my_order = gate_api.post_order(coin_name,"sell","market",available_quantity)
            break  # Exit the loop after selling
        else:
            print("Market price is not higher than price at buy by 1%. Waiting...")
            time.sleep(1)

if __name__ == "__main__":
    main("10","APU_USDT")






