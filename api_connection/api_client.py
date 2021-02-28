import threading
import time
import enum
from math import isclose

import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
from .api_secrets import API_KEY, API_SECRET


class OrderType(enum.Enum):
    MARKET_BUY  = 1
    MARKET_SELL = 2
    BUY_LIMIT   = 3
    SELL_LIMIT  = 4


class ApiClient:

    def __init__(self):
        self._client = None
        self._lock = threading.Lock()
        self._orders_since_run = []

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

    def get_all_orders(self, symbol='ETHUSDT'):
        return self._client.get_all_orders(symbol=symbol)

    def verify_limit_order(self, symbol, order_id):
        print(f"Verifying order ID {order_id}")
        order_recorded = False
        order_status = None
        while not order_recorded:
            try:
                time.sleep(2)
                order_status = self._client.get_order(symbol=symbol, orderId=order_id)
            except BinanceAPIException as e:
                print(f"get_order failed: {e}")
                time.sleep(5)
            except Exception as e:
                print(f"Unexpected error: {e}")
                return False

        if order_status is None:
            print("Order status is None!")
            return False

        while order_status['status'] != 'FILLED':
            try:
                order_status = self._client.get_order(symbol=symbol, orderId=order_id)
                time.sleep(1)
            except BinanceAPIException as e:
                print(e)
                time.sleep(2)
            except Exception as e:
                print(f"Unexpected error: {e}")
                return False

        return True

    def _execute_market_buy(self, symbol, quantity):
        api_res = None
        try:
            api_res = self._client.order_market_buy(symbol=symbol, quantity=quantity)
            print(f"API result: {api_res}")
        except BinanceAPIException as e:
            print(f"Binance error: {e} - Error code: - {e.code}")
            if e.code == -2010: # Account has insufficient balance for requested action
                print("No money.")
                return False
        except Exception as e:
            print(f"Unexpected error: {e}")

        return api_res

    def _execute_market_sell(self, symbol, quantity):
        api_res = None
        try:
            api_res = self._client.order_market_sell(symbol=symbol, quantity=quantity)
            print(f"API result: {api_res}")
        except BinanceAPIException as e:
            print(f"Binance error: {e} - Error code: - {e.code}")
            if e.code == -2010: # Account has insufficient balance for requested action
                print("No money.")
                return False
        except Exception as e:
            print(f"Unexpected error: {e}")

        return api_res

    def market_sell(self, symbol=None, quantity=None):
        if symbol is None or quantity is None:
            raise ValueError("You MUST pass symbol and quantity. Be careful with this method!")

        current_balance = self.get_asset_balance(asset=symbol.replace('USDT', ''))['free']
        print(f"Starting balance: {current_balance} {symbol}")

        if float(current_balance) < quantity:
            print(f"Cannot sell {quantity} when there is only {current_balance} available")
            return False

        api_res = False
        for i in range(5):
            api_res = self._execute_market_sell(symbol, quantity)
            if api_res:
                break
            else:
                print(f"Market sell failed. Attempt number {i+1}")

        if not api_res:
            print("Error sending market sell")
            return False

        print(f"Sell order for {quantity} {symbol} filled. Order ID: {api_res['orderId']}")

        after_sell_balance = self.get_asset_balance(asset=symbol.replace('USDT', ''))['free']
        print(f"Balance after sell order: {after_sell_balance} {symbol}")

        if isclose(float(current_balance) - quantity, float(after_sell_balance), abs_tol=1):
            print("Market sell order success")

        return api_res


    def market_buy(self, symbol=None, quantity=None):
        if symbol is None or quantity is None:
            raise ValueError("You MUST pass symbol and quantity. Be careful with this method!")

        current_balance = self.get_asset_balance(asset=symbol.replace('USDT', ''))['free']
        print(f"Starting balance: {current_balance} {symbol}")

        api_res = False
        for i in range(5):
            api_res = self._execute_market_buy(symbol, quantity)
            if api_res:
                break
            else:
                print(f"Market buy failed. Attempt number {i+1}")

        if not api_res:
            print("Error sending market buy")
            return False

        # print("Verifying market buy order")
        # order_verified = self.verify_order(symbol, api_res['orderId'])
        # if not order_verified:
        #     print(f"Order {api_res['orderId']} verification failed")
        # else:
        #     print(f"Buy order for {quantity} {symbol} filled. Order ID: {api_res['orderId']}")
        print(f"Buy order for {quantity} {symbol} filled. Order ID: {api_res['orderId']}")

        after_buy_balance = self.get_asset_balance(asset=symbol.replace('USDT', ''))['free']
        print(f"Balance after buy order: {after_buy_balance} {symbol}")

        if isclose(float(current_balance) + quantity, float(after_buy_balance), abs_tol=1):
            print("Market buy order success")

        return api_res


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




