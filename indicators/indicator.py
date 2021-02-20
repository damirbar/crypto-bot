
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

    def action_expedience(self):
        """
        :return: dictionary of expedience - buy or sale, each in range [0,1]. One of the will always be zero.
        """
        raise NotImplementedError
