from datetime import datetime
from data.time_series_data import DataObject

intervals = ("1min",
             "5min",
             "15min",
             "30min",
             "60min",
             "daily",
             "weekly",
             "monthly"
             "yearly")


class BarContainer(DataObject):

    """
        bars: List of Bar objects

    """

    def __init__(self, bars, interval):
        super().__init__(interval)
        assert isinstance(bars, list)
        assert interval in intervals
        self.data = bars

    @property
    def datetime(self):
        return [b.datetime for b in self.data]

    @property
    def open(self):
        return [b.open for b in self.data]

    @property
    def close(self):
        return [b.close for b in self.data]

    @property
    def high(self):
        return [b.high for b in self.data]

    @property
    def low(self):
        return [b.low for b in self.data]

    @property
    def volume(self):
        return [b.volume for b in self.data]


class Bar:

    """
    Representing each bar in the candlestick plot

    Member variables:
        - Timestamp: Timestamp of bar as datetime object
        - Open: Open price of the bar
        - Close: Closing price of the bar
        - High: High price of the bar
        - Low: Low price of the bar
        - Volume: Volume traded of the bar

    """

    def __init__(self, timestamp, opn, close, high, low, volume):
        super().__init__()
        self.datetime = timestamp
        self.open = float(opn)
        self.close = float(close)
        self.high = float(high)
        self.low = float(low)
        self.volume = int(volume)

        assert isinstance(timestamp, datetime) or timestamp is None
        assert isinstance(self.open, float)
        assert isinstance(self.high, float)
        assert isinstance(self.low, float)
        assert isinstance(self.close, float)
        assert isinstance(self.volume, int)

    def __add__(self, other):
        timestamp = max(self.datetime, other.datetime)
        opn = self.open + other.open
        close = self.close + other.close
        high = self.high + other.high
        low = self.low + other.low
        volume = self.volume + other.volume

        return Bar(timestamp, opn, close, high, low, volume)

    def __truediv__(self, f):
        assert isinstance(f, int) or isinstance(f, float)
        return Bar(self.datetime, self.open / f, self.close / f, self.high / f, self.low / f, self.volume / f)

    def __mul__(self, f):
        assert isinstance(f, int) or isinstance(f, float)
        return Bar(self.datetime, self.open * f, self.close * f, self.high * f, self.low * f, self.volume * f)