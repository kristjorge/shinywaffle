from tools.api_link import APILink
from datetime import datetime
from common.event.events import TimeSeriesEvent


class DataProvider:

    def __init__(self, context, assets):
        self.assets = assets
        self.context = context

    def get_time_series_data(self):
        raise NotImplemented


class BacktestDataProvider(DataProvider):

    def __init__(self, context, assets, times: list):
        super().__init__(context, assets)
        self.times = times
        self.current_time = datetime(1900, 1, 1, 0, 0, 0)
        assert isinstance(self.assets, dict)

    def get_time_series_data(self):

        """
        Gathering a dictionary of the time series data for all the stocks in the backtester
        "times" stores the historical report steps generated in the backtester. Every time this method is called,
        the first item is popped to advance the historical time. When all the items are popped, then the backtest
        stops.

        Creates a dict (time_series_data) which holds the keys 'current time' (popped time) and keys for each ticker
        of the active assets. Each ticker key is a new dict with the time series data under each key.

        :return: dict with TimeSeriesEvents for each asset that has seen a new event
        """

        try:
            new_time = self.times.pop(0)
        except IndexError:
            raise BacktestCompleteException
        else:

            time_series_data = {}
            time_series_events = []
            time_series_data['current time'] = new_time

            for asset in self.assets.values():
                time_series_data[asset.ticker] = {}
                time_series = asset.data.time_series()
                time_series.append(("bars", asset.bars))

                # Aggregating time series data to be used in event handler
                for series in time_series:
                    time_series_data[asset.ticker][series[0]] = series[1].sample_datetime(new_time)

                # If there are any items in a list consisting of data series elements between the previous time and
                # the new current time, then add a TimeSeriesEvent and break the loop for that asset
                for series in time_series:
                    if [s for s in series[1] if self.current_time < s.time <= new_time]:
                        time_series_events.append(TimeSeriesEvent(asset))
                        break

            self.current_time = time_series_data['current time']
            return time_series_events, time_series_data


class LiveDataProvider(DataProvider):

    def __init__(self, context, assets, sleep_time: int = 300):
        assert all(isinstance(asset.bars, APILink) for asset in assets.values())
        super().__init__(context, assets)
        self.sleep_time = sleep_time
        self.latest_timestamp = datetime(1900, 1, 1)

    def get_time_series_data(self):
        time_series_data = {}
        time_series_events = []

        for asset in self.assets.values():
            time_series_data[asset.ticker] = {}
            avail_series = [(s, getattr(asset.data, s)) for s in dir(asset.data) if isinstance(getattr(asset.data, s), APILink)]
            for series in avail_series:
                time_series_data[asset.ticker][series[0]] = series[1].fetch()

            time_series_data[asset.ticker]['bars'] = asset.bars.fetch()

            # Add new time series event only if a fresh bar has been found
            # TODO: Verify if this really makes sense
            if time_series_data[asset.ticker]['bars'][0].time != self.latest_timestamp:
                print("New bar observed. Creating time series event...")
                time_series_events.append(TimeSeriesEvent(asset))

            self.latest_timestamp = time_series_data[asset.ticker]['bars'][0].time
            time_series_data['current time'] = time_series_data[asset.ticker]['bars'][0].time
        return time_series_events, time_series_data


class BacktestCompleteException(Exception):
    def __init__(self):
        super().__init__()
        print("Backtest complete!")
