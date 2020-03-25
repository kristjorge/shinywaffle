import abc
from tools.api_link import APILink
from data.time_series_data import DataSeries
from datetime import datetime
from event.events import TimeSeriesEvent


class DataProvider(abc.ABC):

    def __init__(self, assets):
        self.assets = assets

    @abc.abstractmethod
    def detect_time_series_event(self):
        pass

    @abc.abstractmethod
    def get_time_series_data(self):
        pass


class BacktestDataProvider(DataProvider):

    def __init__(self, assets, times):
        super().__init__(assets)
        self.times = times
        self.current_time = datetime(1900, 1, 1, 0, 0, 0)
        assert isinstance(self.assets, dict)

    def detect_time_series_event(self):

        """
        Gathering a dictionary of the time series data for all the stocks in the backtester
            "times" stores the historical report steps generated in the backtester. Every time this method is called,
            the first item is popped to advance the historical time. When all the items are popped, then the backtest
            stops.
        :return: dict with TimeSeriesEvents for each asset that has seen a new event
        """

        time_series_data = {}
        time_series_events = []
        new_time = self.times.pop(0)
        time_series_data["times"] = new_time

        for asset in self.assets.values():
            time_series = asset.data.time_series()
            time_series.append(("bars", asset.bars))

            for series in time_series:
                if [s for s in series[1] if self.current_time < s.datetime <= new_time]:
                    time_series_events.append(TimeSeriesEvent(asset))
                    break

        self.current_time = time_series_data["times"]
        return time_series_events

    def get_time_series_data(self):
        """

        :return: time_series_data as a dictionary with keys of asset.ticker. Each value is a dictionary with
                 keys with the name of the data series in the time_series
        """
        time_series_data = {}
        for asset in self.assets.values():

            time_series_data[asset.ticker] = {}
            time_series = asset.data.time_series()
            time_series.append(("bars", asset.bars))

            for series in time_series:
                time_series_data[asset.ticker][series[0]] = series[1].sample_datetime(self.current_time)

        return time_series_data

    @property
    def backtest_is_active(self):
        if self.times:
            return True
        else:
            return False


class LiveDataProvider(DataProvider):

    def __init__(self, assets):
        assert all(isinstance(asset.bar, APILink) for asset in assets)
        super().__init__(assets)

    def detect_time_series_event(self):
        pass

    def get_time_series_data(self):
        pass

