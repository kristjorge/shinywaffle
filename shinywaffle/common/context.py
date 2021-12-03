from __future__ import annotations
import copy
from shinywaffle.common.assets import Asset
from collections import defaultdict
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from shinywaffle.data.time_series_data import TimeSeries, TimeSeriesType
    from shinywaffle.common.broker import BacktestBroker
    from shinywaffle.common.account import Account


class Context:

    """
    Context class representing a holder for assets, broker and account. This object will be
    """

    def __init__(self):
        from shinywaffle.data.time_series_data import TimeSeriesContainer
        self.assets = {}
        self.strategies = {}
        self.broker = None
        self.account = None
        self.risk_manager = None
        self.time_series = defaultdict(lambda: TimeSeriesContainer())
        self.time = datetime(1900, 1, 1)
        self.times = list()

    def set_broker(self, broker: BacktestBroker) -> None:
        self.broker = broker

    def set_account(self, account: Account) -> None:
        self.account = account
        self.risk_manager = account.risk_manager

    def update_time(self, time: datetime) -> None:
        """ Saves the current time to the list of datetimes and changes self.time to the newly provided timestamp"""
        self.times.append(self.time)
        self.time = time

    def copy(self) -> Context:
        return copy.deepcopy(self)

    def save_time_series(self, asset: Asset, time_series: TimeSeries, series_type: TimeSeriesType) -> None:
        """
        Save the time series to the context on the asset ticker key.
        Also save the same TimeSeries object in the asset's TimeSeriesContainer
        """
        from shinywaffle.data.time_series_data import TimeSeries
        self.time_series[asset.ticker].add(time_series=time_series, series_type=series_type)
        new_time_series = TimeSeries(id=time_series.uuid)
        asset.data.add(time_series=new_time_series, series_type=series_type)
