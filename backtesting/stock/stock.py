from utils.bar import BarHolder
from utils.time_series_data import TimeSeriesDataHolder
from utils.time_series_data import TimeSeriesData
from backtesting.stock.stops import StopHolder
from backtesting.stock.stops import TrailingStop
from backtesting.stock.stops import StopLoss
from backtesting.stock.stops import TargetStop

intervals = ("1min",
             "5min",
             "15min",
             "30min",
             "60min",
             "daily",
             "weekly",
             "monthly"
             "yearly")


class Stock:

    """
    Class representing a tradable stock

    Member variables
        - ticker (string):
            Stock ticker

        - name (string)
            Name of the stock

        - strategies (dict)
            Dict of strategy objects

        - bars (BarContainer)
            Price data

    """

    def __init__(self, name, ticker):
        self.name = name
        self.ticker = ticker
        self.series = TimeSeriesDataHolder()
        self.stops = StopHolder()
        self.datetime_format = "%Y-%m-%d"

    def set_bars(self, bars, interval):
        assert isinstance(bars, BarHolder)
        assert isinstance(interval, str) and interval in intervals
        self.series.add(bars, "bars")

    def add_time_series(self, name, data_series):
        assert isinstance(data_series, TimeSeriesData)
        self.series.add(data_series, name)

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
        }
        return data
