import abc
from utils.time_series_data import TimeSeriesDataHolder
from backtesting.stock.stops import StopHolder

intervals = ("1min",
             "5min",
             "15min",
             "30min",
             "60min",
             "daily",
             "weekly",
             "monthly"
             "yearly")


class FinancialAsset(abc.ABC):

    """

    Base class for tradable financial_assets. Classes that inherit from financial_assets are:
        - Stocks
        - Forex
        - Cryptocurrencies
        - Derivatives

"""

    def __init__(self, name, ticker, base_currency):
        self.name = name
        self.ticker = ticker
        self.base_currency = base_currency
        self.series = TimeSeriesDataHolder()
        self.stops = StopHolder()

    def self2dict(self):
        data = {
            'name': self.name,
            'ticker': self.ticker,
            'base_currency:': self.base_currency
        }
        return data
