import abc
from data.time_series_data import DataSeries
from backtesting.stock.stops import TrailingStop
from backtesting.stock.stops import StopLoss
from backtesting.stock.stops import TargetStop
from backtesting.stock.stops import StopHolder
from data.bar import BarContainer
from data.time_series_data import DataSeriesContainer
from tools.api_link import APILink

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
"""

    def __init__(self, name, ticker, base_currency):
        self.name = name
        self.ticker = ticker
        self.base_currency = base_currency
        self.datetime_format = "%Y-%m-%d"
        self.bars = None
        self.data = DataSeriesContainer()
        self.stops = StopHolder()

    def set_bars(self, bars):
        assert isinstance(bars, BarContainer) or isinstance(bars, APILink)
        self.bars = bars

    def add_data_object(self, name, data_series):
        assert isinstance(data_series, DataSeries)
        self.data.add(data_series, name)

    def set_stop(self, stop_object):
        if isinstance(stop_object, StopLoss):
            setattr(self.stops, "stop_loss", stop_object)
        elif isinstance(stop_object, TrailingStop):
            setattr(self.stops, "trailing_stop", stop_object)
        elif isinstance(stop_object, TargetStop):
            setattr(self.stops, "target_stop", stop_object)

    def self2dict(self):
        data = {
            'name': self.name,
            'ticker': self.ticker,
            'base_currency:': self.base_currency
        }
        return data


class Stock(FinancialAsset):

    def __init__(self, name, ticker, base_currency):
        super().__init__(name, ticker, base_currency)
        self.type = "stock"


class Forex(FinancialAsset):

    def __init__(self, name, ticker, base_currency):
        super().__init__(name, ticker, base_currency)
        self.type = "forex"


class Cryptocurrency(FinancialAsset):

    def __init__(self, name, ticker, base_currency):
        super().__init__(name, ticker, base_currency)
        self.type = "cryptocurrency"

