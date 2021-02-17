
class TradingIndicator:

    def __init__(self):
        self._sequence = None

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value

    def initialize_indicator(self):
        pass
