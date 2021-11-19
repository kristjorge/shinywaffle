from __future__ import annotations
from datetime import datetime
from shinywaffle.common.context import Context
from collections import defaultdict
from typing import List, Optional
from enum import Enum
import uuid


class TimeSeriesType(Enum):
    """
    Enum for type of time series that exist.

        - Asset bars is the TimeSeries object for the bars of the asset
        - Associated bars is the TimeSeries object for bars of an associated asset that is used in a trading strategy
        - Associated is the TimeSeries object for an associated time series which is not a bar type. This can be
        anything from sentiment timeseries to earnings reports etc

    """
    TYPE_ASSET_BARS = 'asset bars'
    TYPE_ASSOCIATED_BARS = 'associated bars'
    TYPE_ASSOCIATED = 'associated'


class TimeSeries:

    """
    A container class for time series data.

    Calling the ordinary list methods on self returns the methods called on the data in self.data

    """

    def __init__(self, id: Optional[uuid.UUID] = None):
        self.data = list()
        if id is not None:
            self.uuid = id
        else:
            self.uuid = uuid.uuid4()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __iter__(self):
        for d in self.data:
            yield d

    def extend(self, other):
        if type(other) == list:
            other.reverse()
            for data_point in other:
                self.data.insert(0, data_point)
        if other:
            self.update_attributes(other[0])

    def retrieve(self, from_time: datetime, to_time: datetime) -> list:
        return [d for d in self.data if from_time < d.time <= to_time]

    def set(self, data: list) -> None:

        """
        Setting self.data equals to the data argument.
        In addition this method creates attributes for the attributes for the items in the data list
        :param data: List of data points (not necessarily the class below)
        """
        self.data = data
        self.update_attributes(self.data[0])

    def update_attributes(self, data_point):
        """ Sets member variables on the TimeSeries object for each of the member variables of the member variables
        in the TimeSeries data objects. The member variables on the TimeSeries object returns the list of all the
        data object's same member variables"""
        attributes = [a for a in dir(data_point) if not a.startswith("_")
                      and a not in dir("__builtins__")]

        for attrib in attributes:
            setattr(self, attrib, [getattr(d, attrib) for d in self.data])

    def get(self, attrib_name) -> list:
        """
        :param attrib_name: name of the parameter to be fetched
        :return: returns a list of the data parameter for all objects in self.data
        """
        return [getattr(i, attrib_name) for i in self.data]


class TimeSeriesContainer:

    """
    A container class for data in an financial instrument class.

    Method: add: Adds a new time series to the stock object. Asserts that the added time series data is
            of the type TimeSeriesData
    """

    #intervals = ('1min', '1m',
    #             '3min', '3m',
    #             '5min', '5m',
    #             '15min', '15m',
    #             '30min', '30m',
    #             '60min', '1h',
    #             '2h', '4h', '6h', '8h', '12h',
    #             'daily', '1d', '3d',
    #             'weekly', '1w',
    #             'monthly', '1M',
    #             'yearly')

    def __init__(self):
        """
        Class can either be initialized with or without a list of TimeSeries objects

        self._time_series is a dict with the keys equal to the TimeSeriesType enum types and values are a list
        of TimeSeries

        """
        self._time_series = defaultdict(lambda: list())

    def add(self, time_series: TimeSeries, series_type: TimeSeriesType):
        """ Adds a named TimeSeries object to the DataSeriesContainer object"""
        if not isinstance(time_series, TimeSeries):
            raise TypeError('Data source must be of type TimeSeries')

        if not isinstance(series_type, TimeSeriesType):
            raise TypeError('Series type must be of enum TimeSeriesType')

        if series_type == TimeSeriesType.TYPE_ASSET_BARS and self.get(series_type=TimeSeriesType.TYPE_ASSET_BARS):
            raise AttributeError('Time series of type TimeSeriesType.TYPE_ASSET_BARS already exists in the asset.')

        self._time_series[series_type].append(time_series)

    def get(self, series_type: Optional[TimeSeriesType] = None, id: uuid.UUID = None) -> List[TimeSeries]:
        """
        :return: A list of tuples of the name of the attribute and the attribute object, for all attributes of type
        TimeSeries
        """
        #return [getattr(self, s) for s in dir(self) if isinstance(getattr(self, s), TimeSeries)]

        series = list()
        if series_type is not None:
            series = self._time_series[series_type]
        else:
            for saved_series in self._time_series.values():
                series.extend(saved_series)

        if id is not None:
            for s in series:
                if s.uuid == id:
                    return s
            raise ValueError(f'No TimeSeries object exists with id: {id}')

        else:
            return series

    def __iter__(self):
        for t in self.get():
            yield t


class RetrievedTimeSeriesData:

    def __init__(self, context: Context):
        """
        The self.asset_data is a default dict that creates another default dict that creates a list as the default
        argument.
        :param context:
        """
        super().__init__()
        self.time = datetime(1900, 1, 1, 0, 0, 0)
        self.context = context
        self.asset_data = defaultdict(lambda: defaultdict(lambda: TimeSeries()))

    def __getitem__(self, key):
        return self.asset_data[key]
