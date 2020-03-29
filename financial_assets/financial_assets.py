import abc
from data.time_series_data import DataSeries
from backtesting.stock.stops import TrailingStop
from backtesting.stock.stops import StopLoss
from backtesting.stock.stops import TargetStop
from backtesting.stock.stops import StopHolder
from data.time_series_data import DataSeriesContainer
from tools.api_link import APILink
from strategy.strategy import TradingStrategy


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
        self.strategies = dict()
        self.latest_bar = None

    def set_bars(self, bars):
        assert isinstance(bars, DataSeries) or isinstance(bars, APILink)
        self.bars = bars

    def add_strategy(self, strategy_object):
        assert isinstance(strategy_object, TradingStrategy)
        if strategy_object.name in self.strategies:
            print("Strategy already exists in asset. Skipped.")
        else:
            self.strategies[strategy_object.name] = strategy_object

    def add_data_series(self, name, data_series):
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
        self.lowest_quantity = 1


class Forex(FinancialAsset):

    def __init__(self, name, ticker, base_currency):
        super().__init__(name, ticker, base_currency)
        self.type = "forex"
        self.lowest_quantity = 0.01


class Cryptocurrency(FinancialAsset):

    def __init__(self, name, ticker, base_currency):
        super().__init__(name, ticker, base_currency)
        self.type = "cryptocurrency"
        self.lowest_quantity = 0.000000001

