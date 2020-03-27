import abc


class TradingStrategy(abc.ABC):

    """

Base class for trading strategies used in either backtesting or live trading.
All implemented strategies must inherit from this super class

Functions:
    - link: Link the strategy object to a financial asset object
    - generate_signal: Evaluates data and generates a signal either "buy" or "sell"
    - self2dict: Generating the main meta data for the objects in a dict that can be dumped into a json file

"""

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def generate_signal(self, time_series_data):
        pass

    def self2dict(self):
        data = {
            'name': self.name
        }

        return data



