from actions.cryptoTrader import CryptoTrader
from time import sleep


while True:
        trader = CryptoTrader()
        trader.trade()
        sleep(30)