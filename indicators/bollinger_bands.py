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
        self._dataframe['Lower Band']  = self._dataframe['Middle Band'] - 1.96 * self._dataframe['Close'].rolling(window=self.sessions_back).std()
        self._dataframe['Upper Band']  = self._dataframe['Middle Band'] + 1.96 * self._dataframe['Close'].rolling(window=self.sessions_back).std()

    @property
    def dataframe(self):
        return self._dataframe
