from datetime import datetime


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

    def __init__(self,
                 timestamp: datetime, opn: float or str, close: float or str,
                 high: float or str, low: float or str, volume: float or str):

        super().__init__()
        self.time = timestamp
        self.open = float(opn)
        self.close = float(close)
        self.high = float(high)
        self.low = float(low)
        self.volume = int(volume)

    def __str__(self):
        return f'Bar(time open={self.time}, open={self.open}, close={self.close}, high={self.high}, low={self.low}, volume={self.volume})'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        timestamp = max(self.time, other.time)
        opn = self.open + other.open
        close = self.close + other.close
        high = self.high + other.high
        low = self.low + other.low
        volume = self.volume + other.volume

        return Bar(timestamp, opn, close, high, low, volume)

    def __truediv__(self, f):
        assert isinstance(f, int) or isinstance(f, float)
        return Bar(self.time, self.open / f, self.close / f, self.high / f, self.low / f, self.volume / f)

    def __mul__(self, f):
        assert isinstance(f, int) or isinstance(f, float)
        return Bar(self.time, self.open * f, self.close * f, self.high * f, self.low * f, self.volume * f)
