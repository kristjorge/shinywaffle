from __future__ import annotations
from shinywaffle.tools.api_link import APILink
from shinywaffle.utils.misc import DAILY_DATETIME_FORMAT

from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shinywaffle.common.context import Context
    from shinywaffle.data.time_series_data import TimeSeries, TimeSeriesType


class AssetType(Enum):
    TYPE_STOCK = 'stock'
    TYPE_FOREX = 'forex'
    TYPE_CRYPTOCURRENCY = 'cryptocurrency'


class BaseAsset:
    def __init__(self, num_decimal_points, name: str, initial_balance: float):
        self.name = name
        self.num_decimal_points = num_decimal_points
        self.initial_balance = initial_balance

    def report(self):
        return {'base asset': self.name, 'decimal points': self.num_decimal_points}


class Asset(ABC):

    """
    Base class for tradeable assets. Classes that inherit from assets are:
        - Stocks
        - Forex
        - Cryptocurrencies
    """

    def __init__(self, context: Context, name: str, ticker: str):
        from shinywaffle.data.time_series_data import TimeSeriesContainer
        self.name = name
        self.ticker = ticker
        self.datetime_format = DAILY_DATETIME_FORMAT
        self.data = TimeSeriesContainer()
        context.assets[self.ticker] = self

    @property
    def bars(self) -> TimeSeries:
        """ The bars are returned from the time series container"""
        from shinywaffle.data.time_series_data import TimeSeriesType
        return self.data.get(series_type=TimeSeriesType.TYPE_ASSET_BARS)[0]

    def __repr__(self):
        return '{}: {}'.format(self.ticker, self.name)

    def report(self) -> dict:

        """
        Returning a serializable dictionary that can be reported in a json file by the reporter class
        :return: data (dictionary)
        """

        data = {
            'name': self.name,
            'ticker': self.ticker
        }
        return data


class Stock(Asset):
    def __init__(self, context, name, ticker):
        super().__init__(context, name, ticker)
        self.type = AssetType.TYPE_STOCK
        self.num_decimal_points = 0


class Forex(Asset):

    def __init__(self, context, name, ticker):
        super().__init__(context, name, ticker)
        self.type = AssetType.TYPE_FOREX
        self.num_decimal_points = 2


class Cryptocurrency(Asset):

    def __init__(self, context, name, ticker):
        super().__init__(context, name, ticker)
        self.type = AssetType.TYPE_CRYPTOCURRENCY
        self.num_decimal_points = 8


class USD(BaseAsset):
    def __init__(self, initial_balance: float):
        BaseAsset.__init__(self, num_decimal_points=2, name='USD', initial_balance=initial_balance)


class USDT(BaseAsset):
    def __init__(self, initial_balance: float):
        BaseAsset.__init__(self, num_decimal_points=2, name='USD Tether', initial_balance=initial_balance)


class BTC(BaseAsset):
    def __init__(self, initial_balance: float):
        BaseAsset.__init__(self, num_decimal_points=8, name='Bitcoin', initial_balance=initial_balance)
        self.name = 'Bitcoin'


class ETH(BaseAsset):
    def __init__(self, initial_balance: float):
        BaseAsset.__init__(self, num_decimal_points=8, name='Ethereum', initial_balance=initial_balance)
        self.name = 'Ethereum'