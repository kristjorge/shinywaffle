from data.time_series_data import TimeSeries
from technical_indicators import TooSmallWindowException
import numpy as np


def exponential_moving_average(data_series, window, attributes, offset=0):

    assert isinstance(data_series, TimeSeries)
    assert isinstance(attributes, list) or isinstance(attributes, str)

    if type(attributes) != list:
        attributes = [attributes]

    arrays = []
    for attrib in attributes:
        assert hasattr(data_series[0], attrib), "{} is not an attribute in the data series".format(attrib)
        arrays.append(np.array(getattr(data_series, attrib)[offset:offset + window]))

    avg_array = sum(arrays) / len(arrays)
    k = 2 / (window + 1)
    ema_list = [0]*avg_array.size
    ema_list[-1] = avg_array[-1]
    for i, ema in reversed(list(enumerate(ema_list))):
        if i == len(ema_list)-1:
            continue
        else:
            ema_list[i] = avg_array[i]*k + ema_list[i+1] * (1-k)

    if len(ema_list) >= window:
        return ema_list[0]
    else:
        return TooSmallWindowException
