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

    def get_current_price(self, symbol):
        return float(self._client.get_symbol_ticker(symbol=symbol)['price'])

    def get_candles(self, symbol='ETHUSDT', interval='1m'):
        klines = self._client.get_klines(symbol=symbol, interval=interval, limit=500)
        return [BinanceCandleStick(a[1], a[2], a[3], a[4]) for a in klines]


class BinanceCandleStick:
    def __init__(self, open, high, low, close):
        self.open  = open
        self.high  = high
        self.low   = low
        self.close = close

    def __repr__(self):
        return f'<Open: {self.open}, High: {self.high}, Low: {self.low}, Close: {self.close}>'




