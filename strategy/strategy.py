import abc
from financial_assets.stock import Stock

""" 

Base class for trading strategies used in either backtesting or live trading.
All implemented strategies must inherit from this super class 

Functions:
    - read: Returns the TradingStrategy object 
    - generate_signal: Evaluates data and generates a signal either "buy" or "sell"


"""


class TradingStrategy(abc.ABC):

    def __init__(self, name):
        self.name = name
        self.stocks = dict()

    @abc.abstractmethod
    def generate_signal(self):
        pass

    def link_stock(self, stock):
        assert isinstance(stock, Stock)
        assert stock.name
        assert stock.ticker

        self.stocks[stock.ticker] = stock

    def self2dict(self):
        data = {
            'name': self.name,
            'stocks linked': ["{} - {}".format(stock.ticker, stock.name) for stock in self.stocks.values()]
        }

        return data



