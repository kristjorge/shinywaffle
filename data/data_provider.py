import abc
from data.time_series_data import DataObject
from datetime import datetime
from event.event import TimeSeriesEvent


class DataProvider(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def detect_time_series_event(self):
        pass


class BacktestingDataProvider(DataProvider):

    def __init__(self, assets, times):
        super().__init__()
        self.assets = assets
        self.times = times
        self.latest_past_time = datetime(1900, 1, 1)

        assert isinstance(self.assets, dict)

    def detect_time_series_event(self):

        """
        Gathering a dictionary of the time series data for all the stocks in the backtester
            "times" stores the historical report steps generated in the backtester. Every time this method is called,
            the first item is popped to advance the historical time. When all the items are popped, then the backtest
            stops.
        :return: dict with TimeSeriesEvents for each asset that has seen a new event
        """

        time_series_data = dict()
        time_series_events = list()
        new_time = self.times.pop(0)
        time_series_data["times"] = new_time

        for asset in self.assets.values():
            time_series = [(s, getattr(asset.series, s)) for s in dir(asset.series) if
                           isinstance(getattr(asset.series, s), DataObject)]

            for series in time_series:
                series_list = [s for s in series[1] if self.latest_past_time < s.datetime <= new_time]

                if series_list:
                    time_series_events.append(TimeSeriesEvent(asset.name))
                    continue

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

