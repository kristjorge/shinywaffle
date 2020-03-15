from financial_assets.financial_asset import FinancialAsset
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


class Stock(FinancialAsset):

    """
    Class representing a common stock extending the FinancialAsset base class

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

    def __init__(self, name, ticker, base_currency):
        super().__init__(name, ticker, base_currency)
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
