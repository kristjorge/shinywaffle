from data.time_series_data import DataSeries
import numpy as np


def exponential_moving_average(data_series, window, attributes, offset=0):

    assert isinstance(data_series, DataSeries)
    assert isinstance(attributes, list)

    arrays = []
    ema_list = [0]*window
    for attrib in attributes:
        assert hasattr(data_series[0], attrib), "{} is not an attribute in the data series".format(attrib)
        arrays.append([getattr(data_series, attrib)[offset:offset + window]])

    average = np.mean(sum(arrays) / len(arrays))
    arr = np.array(average)
    k = 2 / (window + 1)

    for i, ema in reversed(ema_list):
        if i == -1:
            ema = arr[-1]
        else:
            ema = arr[i]*k + ema[i-1] * (1-k)

    return ema_list[0]
