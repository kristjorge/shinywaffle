import pandas as pd
from datetime import datetime
from shinywaffle.utils.misc import get_datetime_format
from shinywaffle.common.context import Context
from _collections import defaultdict


class DataSeriesContainer:

    """
    A container class for data in an financial instrument class.

    Method: add_time_series: Adds a new time series to the stock object. Asserts that the added time series data is
            of the type TimeSeriesData
    """

    intervals = ('1min', '1m',
                 '3min', '3m',
                 '5min', '5m',
                 '15min', '15m',
                 '30min', '30m',
                 '60min', '1h',
                 '2h', '4h', '6h', '8h', '12h',
                 'daily', '1d', '3d',
                 'weekly', '1w'
                 'monthly', '1M'
                 'yearly')

    def __init__(self):
        pass

    def add(self, data_source, name):
        assert isinstance(data_source, TimeSeries)
        setattr(self, name, data_source)

    def time_series(self):
        """
        :return: A list of tuples of the name of the attribute and the attribute object, for all attributes of type
        TimeSeries
        """
        return [(s, getattr(self, s)) for s in dir(self) if isinstance(getattr(self, s), TimeSeries)]

    def __iter__(self):
        for t in self.time_series():
            yield t


class TimeSeries:

    """
    A container class for time series data.
    Inherits from list builtin type.

    Calling the ordinary list methods on self returns the methods called on the data in self.data

    """

    def __init__(self):
        self.data = list()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __iter__(self):
        for d in self.data:
            yield d

    def extend(self, other):
        if type(other) == list:
            # self.data += other
            other.reverse()
            for data_point in other:
                self.data.insert(0, data_point)
        if other:
            self.update_attributes(other[0])

    def retrieve(self, from_time: datetime, to_time: datetime):
        return [d for d in self.data if from_time < d.time <= to_time]

    def set(self, data):

        """
        Setting self.data equals to the data argument.
        In addition this method creates attributes for the attributes for the items in the data list
        :param data: List of data points (not necessarily the class below)
        :return: None
        """

        # from tools.api_link import APILink
        # assert isinstance(data, list) or isinstance(data, APILink)
        self.data = data
        self.update_attributes(self.data[0])

    def update_attributes(self, data_point):
        attributes = [a for a in dir(data_point) if not a.startswith("_")
                      and a not in dir("__builtins__")]

        for attrib in attributes:
            setattr(self, attrib, [getattr(d, attrib) for d in self.data])

    def get(self, attrib_name):
        """
        :param attrib_name: name of the parameter to be fetched
        :return: returns a list of the data parameter for all objects in self.data
        """
        return [getattr(i, attrib_name) for i in self.data]


class DataPoint:

    """
    A container object for a data point.
    """

    def __init__(self, data_dict):
        """

        Asserting that datetime is among the keys in the data_dict and that it is of the type datetime

        :param data_dict: a dictionary of data to be set as object attributes
        """
        assert isinstance(data_dict, dict)
        assert "datetime" in data_dict.keys()
        assert isinstance(data_dict["datetime"], datetime)
        for key in data_dict.keys():
            if key != "datetime":
                setattr(self, key, float(data_dict[key]))

        # Setting datetime separately
        setattr(self, "datetime", data_dict["datetime"])


class TimeSeriesDataReader:

    """
    Class that reads time series data in the form of a CSV file
    Returns a TimeSeriesData object with the time series data
    """

    def __init__(self):
        pass

    @staticmethod
    def read_csv(csv_path, interval):
        assert isinstance(csv_path, str)
        df = pd.read_csv(csv_path)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        cols = [col for col in df.columns]
        assert cols[0] == "datetime", "First column must be a called datetime"

        data_objects = list()
        datetime_format = get_datetime_format(interval)

        for row in df.itertuples(index=False):
            row_data = {col: getattr(row, col) for col in cols if col != "datetime"}
            row_data["datetime"] = datetime.strptime(getattr(row, "datetime"), datetime_format)
            data_objects.append(DataPoint(row_data))

        time_series_data = TimeSeries()
        time_series_data.set(data_objects)
        return time_series_data


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
