
class Bot:

    def __init__(self):
        self.indicators = []

    def add_strategy(self, strategy):
        self.indicators.append(strategy)

    def initialize_strategies(self):
        for indicator in self. strategies:
            indicator.initialize_indicator()


