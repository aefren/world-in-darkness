import json
from pdb import Pdb
import requests



r = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/')
for coin in r.json():
    print(coin["price_usd"])