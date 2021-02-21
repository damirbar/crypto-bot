from .indicator import TradingIndicator


class RSI(TradingIndicator):

    def __init__(self, dataframe):
        super().__init__()

        self._std_spacing   = 1.96
        self._sessions_back = 20
        self._dataframe     = dataframe

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

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, df):
        self._dataframe = df
        self.initialize_indicator()

    def action_expedience(self):
        pass
