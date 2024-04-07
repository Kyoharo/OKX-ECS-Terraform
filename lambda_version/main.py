from actions.cryptoTrader import CryptoTrader
from time import sleep
# def lambda_handler(event, context):
#         trader = CryptoTrader()
#         trader.trade()
        
#         return {
#             'statusCode': 200,
#             'body': json.dumps('Lambda function executed successfully')
#         }

while True:
        trader = CryptoTrader()
        trader.trade()
        sleep(30)