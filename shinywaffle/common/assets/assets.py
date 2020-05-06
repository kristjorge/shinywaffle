from shinywaffle.data.time_series_data import TimeSeries
from shinywaffle.backtesting.stock.stops import TrailingStop
from shinywaffle.backtesting.stock.stops import StopLoss
from shinywaffle.backtesting.stock.stops import TargetStop
from shinywaffle.backtesting.stock.stops import StopHolder
from shinywaffle.data.time_series_data import DataSeriesContainer
from shinywaffle.tools.api_link import APILink
from shinywaffle.utils.misc import daily_datetime_format
from shinywaffle.common.context import Context


class BaseAsset:
    def __init__(self, num_decimal_points):
        self.name = None
        self.is_base_asset = True
        self.num_decimal_points = num_decimal_points

    def report(self):
        return {'base asset': self.name, 'decimal points': self.num_decimal_points}


class Asset:

    """
    Base class for tradable assets. Classes that inherit from assets are:
        - Stocks
        - Forex
        - Cryptocurrencies
    """

    def __init__(self, context: Context, name: str, ticker: str, base_currency: BaseAsset):
        self.name = name
        self.ticker = ticker
        self.base_currency = base_currency
        self.datetime_format = daily_datetime_format
        self.bars = None
        self.data = DataSeriesContainer()
        self.stops = StopHolder()
        self.latest_bar = None
        context.assets[self.ticker] = self

    def __repr__(self):
        return '{}: {}'.format(self.ticker, self.name)

    def set_bars(self, bars):
        assert isinstance(bars, TimeSeries) or isinstance(bars, APILink)
        self.bars = bars

    def add_data_series(self, name, data_series):

        """
        Method to add data series to the financial asset. Data series represent time series data like price data
        or sentiment data
        :param name: Name to be referenced
        :param data_series: DataSeries object
        """

        assert isinstance(data_series, TimeSeries)
        self.data.add(data_series, name)

    def set_stop(self, stop_object):
        if isinstance(stop_object, StopLoss):
            setattr(self.stops, "stop_loss", stop_object)
        elif isinstance(stop_object, TrailingStop):
            setattr(self.stops, "trailing_stop", stop_object)
        elif isinstance(stop_object, TargetStop):
            setattr(self.stops, "target_stop", stop_object)

    def report(self):

        """
        Returning a serializable dictionary that can be reported in a json file by the reporter class
        :return: data (dictionary)
        """

        data = {
            'name': self.name,
            'ticker': self.ticker,
            'base_currency:': self.base_currency.report()
        }
        return data


class Stock(Asset):

    def __init__(self, context, name, ticker, base_currency):
        super().__init__(context, name, ticker, base_currency)
        self.type = "stock"
        self.num_decimal_points = 0


class Forex(Asset):

    def __init__(self, context, name, ticker, base_currency):
        super().__init__(context, name, ticker, base_currency)
        self.type = "forex"
        self.num_decimal_points = 2


class Cryptocurrency(Asset):

    def __init__(self, context, name, ticker, base_currency):
        super().__init__(context, name, ticker, base_currency)
        self.type = "cryptocurrency"
        self.num_decimal_points = 8


class USD(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 2)
        self.name = 'USD'


class USDT(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 2)
        self.name = 'USD Tether'


class BTC(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 8)
        self.name = 'Bitcoin'


class ETH(BaseAsset):
    def __init__(self):
        BaseAsset.__init__(self, 8)
        self.name = 'Ethereum'