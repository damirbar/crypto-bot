import threading
import pandas as pd
import numpy as np
from binance.client import Client
from .api_secrets import API_KEY, API_SECRET


class ApiClient:

    def __init__(self):
        self._client = None
        self._lock = threading.Lock()

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

    def get_candles(self, symbol='ETHUSDT', interval='1m', limit=500):
        klines = self._client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return [BinanceCandleStick(a[1], a[2], a[3], a[4], a[5], a[8]) for a in klines]

    def get_candles_dataframe(self, symbol='ETHUSDT', interval='1m', limit=500):
        klines = self._client.get_klines(symbol=symbol, interval=interval, limit=limit)
        arr = []
        for candle in klines:
            obj = {'Open': float(candle[1]), 'High': float(candle[2]), 'Low': float(candle[3]),
                   'Close': float(candle[4]), 'Volume': candle[5], 'Number Of Trades': candle[8]}
            arr.append(obj)
        return pd.DataFrame(arr)


    def get_close_prices_dataframe(self, symbol='ETHUSDT', interval='1m', limit=500):
        with self._lock:
            klines = self._client.get_klines(symbol=symbol, interval=interval, limit=limit)
            close_arr = [float(a[4]) for a in klines]
            np_arr = np.array(close_arr)
            data = {'Close': pd.Series(np_arr)}
            return pd.DataFrame(data)



class BinanceCandleStick:
    def __init__(self, open_price, high_price, low_price, close_price, volume, num_of_trades):
        self.open          = open_price
        self.high          = high_price
        self.low           = low_price
        self.close         = close_price
        self.volume        = volume
        self.num_of_trades = num_of_trades

    def __repr__(self):
        return f'<Open: {self.open}, High: {self.high}, Low: {self.low}, Close: {self.close}, Volume: {self.volume},' \
               f' Number of trades: {self.num_of_trades}>'




