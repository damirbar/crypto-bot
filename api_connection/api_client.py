from binance.client import Client
from .api_secrets import API_KEY, API_SECRET

class ApiClient:

    def __init__(self):
        self._client = None

    def connect(self):
        self._client = Client(API_KEY, API_SECRET)

    def get_raw_client(self):
        return self._client

    def get_asset_balance(self, asset):
        if self._client is None:
            print("client is undefined")
            return
        return self._client.get_asset_balance(asset)
    
    def get_balance(self):
        balance = self._client.get_account()
        my_balance = list(filter(lambda coin: float(coin['locked']) != 0 or float(coin['free']) != 0,
            balance['balances']))
        return my_balance







