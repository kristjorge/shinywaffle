import pandas as pd
from datetime import datetime


class TimeSeriesDataHolder:

    """
    A container class for time series data in the stock.

    Method: add_time_series: Adds a new time series to the stock object. Asserts that the added time series data is
            of the type TimeSeriesData
    """

    def __init__(self):
        pass

    def add(self, container_object, name):
        assert isinstance(container_object, TimeSeriesData)
        setattr(self, name, container_object)


class TimeSeriesData(list):

    """
    A container class for time series data.
    Inherits from list built-in type.

    All the time series data is stored under self.data
    Calling the ordinary list methods on self returns the methods called on the data in self.data
    """

    def __init__(self):
        super().__init__()
        self.data = list()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d

    def __getitem__(self, i):
        return self.data[i]

    def set(self, data_list):
        assert isinstance(data_list, list)
        self.data = data_list

    def get(self, data):
        return [getattr(i, data) for i in self.data]


class TimeSeriesDataObject:

    """

    A container object for a time series data point.

    __init__ takes a dictionary with key value pairs of row

    """

    def __init__(self, row_data, datetime_format):
        assert isinstance(row_data, dict)
        for key in row_data.keys():
            if key == "datetime":
                setattr(self, key, datetime.strptime(row_data[key], datetime_format))
            else:
                setattr(self, key, float(row_data[key]))


class TimeSeriesDataReader:

    """
    Class that reads time series data in the form of a CSV file
    Returns a TimeSeriesData object with the time series data
    """

    def __init__(self):
        pass

    @staticmethod
    def read_csv(csv_path, datetime_format):
        assert isinstance(csv_path, str)
        df = pd.read_csv(csv_path)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        cols = [col for col in df.columns]
        assert cols[0] == "datetime", "First column must be a called datetime"

        data_objects = list()

        for row in df.itertuples(index=False):
            row_data = {col: getattr(row, col) for col in cols}
            data_objects.append(TimeSeriesDataObject(row_data, datetime_format))

        time_series_data = TimeSeriesData()
        time_series_data.set(data_objects)

        return time_series_data



