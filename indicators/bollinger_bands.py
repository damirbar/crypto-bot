import numpy as np
import pandas as pd

from .indicator import TradingIndicator


class BollingerBands(TradingIndicator):

    def __init__(self, dataframe):
        super().__init__()

        self._std_spacing   = 1.96
        self._sessions_back = 20
        self._middle_band   = None
        self._lower_band    = None
        self._upper_band    = None
        self._dataframe     = dataframe

    @property
    def std_spacing(self):
        return self._std_spacing

    @std_spacing.setter
    def std_spacing(self, spacing):
        self._std_spacing = spacing

    @property
    def sessions_back(self):
        return self._sessions_back

    @sessions_back.setter
    def sessions_back(self, sessions):
        self._sessions_back = sessions

    def initialize_indicator(self):
        if self._dataframe is None:
            print("No dataframe provided")
            return
        self._dataframe['Middle Band'] = self._dataframe['Close'].rolling(window=self.sessions_back).mean()
        self._dataframe['Lower Band']  = self._dataframe['Middle Band'] - self._std_spacing * self._dataframe['Close']\
            .rolling(window=self.sessions_back).std()
        self._dataframe['Upper Band']  = self._dataframe['Middle Band'] + self._std_spacing * self._dataframe['Close']\
            .rolling(window=self.sessions_back).std()

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, df):
        self._dataframe = df
        self.initialize_indicator()

    def action_expedience(self):
        last_price  = self._dataframe.iloc[-1]
        close_price = last_price['Close']
        upper_band = last_price['Upper Band']
        middle_band = last_price['Middle Band']
        lower_band = last_price['Lower Band']

        print(f"Current price: {close_price}, Upper band: {upper_band}, Middle band: {middle_band}, Lower band: {lower_band}")

        ret = {'buy': 0, 'sell': 0}
        if close_price < middle_band:
            close_low_dist = close_price - lower_band
            # Strong buy
            if close_low_dist < 0:
                ret['buy'] = 1
                return ret

            mid_low_dist = middle_band - lower_band
            ret['buy'] = (mid_low_dist - close_low_dist) / mid_low_dist

        elif close_price > middle_band:
            close_up_dist = close_price - upper_band
            # Strong sell
            if close_up_dist > 0:
                ret['sell'] = 1
                return ret

            mid_up_dist = middle_band - upper_band
            ret['sell'] = (mid_up_dist - close_up_dist) / mid_up_dist

        return ret


