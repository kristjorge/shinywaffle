from utils.time_series_data import TimeSeriesData


class DataProvider:

    def __init__(self):
        pass


class BacktestingDataProvider(DataProvider):

    def __init__(self, stocks, times):
        super().__init__()
        self.stocks = stocks
        self.times = times

        assert isinstance(self.stocks, dict)

    def provide_time_series_data(self):

        """
        Gathering a dictionary of the time series data for all the stocks in the backtester
            "times" stores the historical report steps generated in the backtester. Every time this method is called,
            the first item is popped to advance the historical time. When all the items are popped, then the backtest
            stops.
        :return:
        """

        time_series_data = dict()
        time_series_data["times"] = self.times.pop(0)

        for stock in self.stocks.values:
            time_series = [s for s in dir(stock.series) if isinstance(getattr(stock.series, s), TimeSeriesData)]
            for series in time_series:
                pass



        return True


    @property
    def backtest_is_active(self):
        if self.times:
            return True
        else:
            return False

class LiveDataProvider(DataProvider):

    def __init__(self):
        super().__init__()
