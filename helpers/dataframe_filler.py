from helpers.utils import set_interval
import threading


class DataframeFiller:
    def __init__(self, api_client, dataframe):
        self._api_client = api_client
        self._df = dataframe
        self._lock = threading.Lock()

    @set_interval(60)
    def filler(self, symbol, interval, limit):
        with self._lock:
            self._df = self._api_client.get_close_prices_dataframe(symbol=symbol, interval=interval, limit=limit)

    def get_df(self):
        with self._lock:
            return self._df


