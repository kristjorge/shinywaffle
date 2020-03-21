import pandas as pd
from datetime import datetime
from utils.misc import get_datetime_format



class DataObjectContainer:

    """
    A container class for data in an financial instrument class.

    Method: add_time_series: Adds a new time series to the stock object. Asserts that the added time series data is
            of the type TimeSeriesData
    """

    def __init__(self):
        pass

    def add(self, data_source, name):
        assert isinstance(data_source, DataObject)
        setattr(self, name, data_source)


class DataObject(list):

    """
    A container class for time series data.
    Inherits from list builtin type.

    Calling the ordinary list methods on self returns the methods called on the data in self.data

    """

    def __init__(self, interval):

        """

        :param interval: The interval that the data is in. 1min, 5min, 15min, ...
        """
        super().__init__()
        self.data = list()
        self.interval = interval

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d

    def __getitem__(self, i):
        return self.data[i]

    def set(self, data):
        from tools.api_link import APILink
        assert isinstance(data, list) or isinstance(data, APILink)
        self.data = data

    def get(self, attrib_name):
        """
        Get
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

        time_series_data = DataObject(interval)
        time_series_data.set(data_objects)
        return time_series_data



