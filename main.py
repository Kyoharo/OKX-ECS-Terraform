from actions.cryptoTrader import CryptoTrader
from time import sleep

print("Start")
while True:
        trader = CryptoTrader()
        trader.trade()
        sleep(30)