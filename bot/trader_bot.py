
class Bot:

    def __init__(self):
        self._dataframe = None
        self.indicators = []

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, df):
        self._dataframe = df

    def add_strategy(self, strategy):
        self.indicators.append(strategy)

    def initialize_strategies(self):
        for indicator in self. strategies:
            indicator.initialize_indicator()

    def get_expediences(self):
        expediences = {}
        for indicator in self. strategies:
            expediences[indicator.__class__.__name__] = indicator.action_expedience()

