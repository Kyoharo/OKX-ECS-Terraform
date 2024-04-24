#buy_new_crypto
from actions.post import DataAction
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
passphrase = os.getenv("PASSPHRASE")
unique_names = os.getenv("UNIQUE_NAMES").split(',')
buy_crypto = DataAction(api_key, secret_key, passphrase, live_trading=False)


import datetime
import time
import os

def check_time():
    now = datetime.datetime.now()
    if (now.hour == 11 and now.minute == 59) or (now.hour == 12 and now.minute == 00):
        return True  


def main():
    while True:
        if check_time():
            print("It's 5:13 PM. Running your task.")
            try:
                restuls = buy_crypto.post_order("MERL-USDT", "buy", "market", "28")
                if restuls == "Order placed":
                    os.system("echo 'Task executed'")  # This command just prints 'Task executed' to the console
                    break
            except Exception as e:
                print(e)

        else:
            print("Waiting for the time...")
            time.sleep(5)  # Check every minute

if __name__ == "__main__":
    main()

