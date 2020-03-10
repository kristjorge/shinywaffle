from strategy.strategy import TradingStrategy

"""
This is the code for the SMA crossover strategy
"""


class AverageCrossOver(TradingStrategy):

    def __init__(self, name, short, long):
        super().__init__(name)
        self.short = short
        self.long = long

    def generate_signal(self):
        pass
