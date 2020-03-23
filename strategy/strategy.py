import abc
from financial_assets.financial_assets import FinancialAsset


class TradingStrategy(abc.ABC):

    """

Base class for trading strategies used in either backtesting or live trading.
All implemented strategies must inherit from this super class

Functions:
    - read: Returns the TradingStrategy object
    - generate_signal: Evaluates data and generates a signal either "buy" or "sell"

"""

    def __init__(self, name):
        self.name = name
        self.assets = dict()

    @abc.abstractmethod
    def generate_signal(self, asset):
        pass

    def link(self, asset):
        assert isinstance(asset, FinancialAsset)
        self.assets[asset.ticker] = asset

    def self2dict(self):
        data = {
            'name': self.name,
            'applied to': ["{} - {}".format(asset.ticker, asset.name) for asset in self.assets.values()]
        }

        return data



