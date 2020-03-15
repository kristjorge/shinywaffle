from utils.time_series_data import TimeSeriesData
from datetime import datetime
from event.event import TimeSeriesEvent


class DataProvider:

    def __init__(self):
        pass


class BacktestingDataProvider(DataProvider):

    def __init__(self, stocks, times):
        super().__init__()
        self.stocks = stocks
        self.times = times
        self.latest_past_time = datetime(1900, 1, 1)

        assert isinstance(self.stocks, dict)

    def detect_time_series_event(self):
        """
        Gathering a dictionary of the time series data for all the stocks in the backtester
            "times" stores the historical report steps generated in the backtester. Every time this method is called,
            the first item is popped to advance the historical time. When all the items are popped, then the backtest
            stops.
        :return:
        """

        time_series_data = dict()
        time_series_events = list()
        new_time = self.times.pop(0)
        time_series_data["times"] = new_time
        print(new_time.strftime("%d-%m-%Y"))

        for stock in self.stocks.values():
            # time_series_data[stock.name] = dict()
            time_series = [(s, getattr(stock.series, s)) for s in dir(stock.series) if
                           isinstance(getattr(stock.series, s), TimeSeriesData)]

            for series in time_series:
                series_list = [s for s in series[1] if self.latest_past_time < s.datetime <= new_time]
                # time_series_data[stock.name][series[0]] = series_list

                if series_list:
                    time_series_events.append(TimeSeriesEvent(stock.name))
                    continue

            # if time_series_data[stock.name] is not None:
            #     market_events.append(MarketEvent(stock.name))

        self.latest_past_time = time_series_data["times"]
        return time_series_events

    @property
    def backtest_is_active(self):
        if self.times:
            return True
        else:
            return False


class LiveDataProvider(DataProvider):

    def __init__(self):
        super().__init__()

