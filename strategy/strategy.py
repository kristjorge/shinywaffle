from common.context import Context


class TradingStrategy:

    """

Base class for trading strategies used in either backtesting or live trading.
All implemented strategies must inherit from this super class

Functions:
    - link: Link the strategy object to a financial asset object
    - generate_signal: Evaluates data and generates a signal either "buy" or "sell"
    - self2dict: Generating the main meta data for the objects in a dict that can be dumped into a json file

"""

    def __init__(self, context, name):
        self.name = name
        self.context = context

    def generate_signal(self, time_series_data):
        raise NotImplementedError

    def self2dict(self):

        attributes = [a for a in dir(self) if not a.startswith("__")
                      and not a.startswith("_")
                      and a not in dir("__builtins__")
                      and not hasattr(getattr(self, a), "__call__")]

        data = {a: getattr(self, a) for a in attributes}

        return data



