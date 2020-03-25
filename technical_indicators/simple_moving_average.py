from data.time_series_data import DataSeries
import numpy as np


def simple_moving_average(data_series, window, attributes, offset=0):

    """
    :param data_series: A DataSeries object with the data in it
    :param window: the look back window for computing the moving average
    :param offset: the offset of the start of the window
    :param attributes: list of data attributes that that moving average is calculated from
    :return: the moving average as a float
    """

    assert isinstance(data_series, DataSeries)
    assert isinstance(attributes, list)
    arrays = []

    for attrib in attributes:
        assert hasattr(data_series[0], attrib), "{} is not an attribute in the data series".format(attrib)
        arrays.append(np.array([getattr(data_series, attrib)[offset:offset + window]]))

    average = np.mean(sum(arrays) / len(arrays))
    if arrays[0].size >= window:
        return average
    else:
        return None

