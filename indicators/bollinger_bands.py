import numpy as np
import pandas as pd

from .indicator import TradingIndicator


class BollingerBands(TradingIndicator):

    def __init__(self):
        super().__init__()

        self._std_spacing = 1.96
        self._sessions_back   = 20
        self._middle_band = None
        self._lower_band  = None
        self._upper_band  = None
        self._bands = {}

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
        if self.sequence is None:
            print("No sequence provided")
            return
        self._bands['Middle Band'] = self.sequence.rolling(window=self.sessions_back).mean()
        self._bands['Lower Band']  = self._bands['Middle Band'] - 1.96 * self.sequence.rolling(window=self.sessions_back).std()
        self._bands['Upper Band']  = self._bands['Middle Band'] + 1.96 * self.sequence.rolling(window=self.sessions_back).std()

    @property
    def get_bands(self):
        return self._bands
