import time
import hashlib
import hmac
import requests

class GateAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
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
        url = '/spot/orders'
        query_param = ''
        body = f'{{"text":"t-abc123","currency_pair":"{crypto}","type":"{order_type}","account":"spot","side":"{order_action}","amount":{quantity},"time_in_force":"ioc"}}'

        sign_headers = self.gen_sign('POST', self.prefix + url, query_param, body)
        self.headers.update(sign_headers)

        result = requests.request('POST', self.host + self.prefix + url, headers=self.headers, data=body)
        response_data = result.json()  # Parse JSON response
        print(response_data)
        if result.status_code == 200:
            status = response_data['data'][0]['sMsg']
            return status
        else:
            return "Error: No message available"

    def get_coin(self, coin_name):
        url = '/spot/accounts'
        query_param = ''
        sign_headers = self.gen_sign('GET', self.prefix + url, query_param)
        self.headers.update(sign_headers)
        r = requests.request('GET', self.host + self.prefix + url, headers=self.headers)
        response_data = r.json()
        early_currency_data = next((item for item in response_data if item.get('currency') == coin_name), None)
        return early_currency_data["available"]

# Example usage:
api_key = 'your_api_key'
api_secret = 'your_api_secret'

gate_api = GateAPI(api_key, api_secret)
buy_price = "6450"
available_quantity = gate_api.get_coin("EARLY")
