import abc
from tools.api_link import APILink
from data.time_series_data import DataSeries
from datetime import datetime
from event.event import TimeSeriesEvent


class DataProvider(abc.ABC):

    def __init__(self, assets):
        self.assets = assets

    @abc.abstractmethod
    def detect_time_series_event(self, event_stack):
        pass


class BacktestingDataProvider(DataProvider):

    def __init__(self, assets, times):
        super().__init__(assets)
        self.times = times
        self.latest_past_time = datetime(1900, 1, 1, 0, 0, 0)

        assert isinstance(self.assets, dict)

    def detect_time_series_event(self, event_stack):

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
            time_series = [(s, getattr(asset.data, s)) for s in dir(asset.data) if
                           isinstance(getattr(asset.data, s), DataSeries)]

            time_series.append(("bars", asset.bars))

            for series in time_series:
                if [s for s in series[1] if self.latest_past_time < s.datetime <= new_time]:
                    time_series_events.append(TimeSeriesEvent(asset))
                    break

        self.latest_past_time = time_series_data["times"]
        event_stack.add(time_series_events)
        # return time_series_events

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

    def detect_time_series_event(self, event_stack):
        pass

