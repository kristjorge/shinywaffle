from data.time_series_data import TimeSeries
import numpy as np
import math as m


def rsi(data_series, window, attributes, offset=0):
    """
    Method to calculate RSI (relative strength index) technical indicator.

    :param data_series: a DataSeries object containing the time series data
    :param window: the look back window (usually 14 periods in standard RSI calculations, but no default
    values provided here)
    :param attributes: list of attributes that that should be used (and averaged) to calculate the RSI
    :param offset: the offset from the start of the window
    :return: a RSI number as a float
    """

    assert isinstance(data_series, TimeSeries)
    assert isinstance(attributes, list) or isinstance(attributes, str)

    if type(attributes) != list:
        attributes = [attributes]

    arrays = []
    # Window is extended by 1 in order to calculate the up- or downwards movement in the "window" last time steps
    for attrib in attributes:
        assert hasattr(data_series[0], attrib), "{} is not an attribute in the data series".format(attrib)
        arrays.append(np.array(getattr(data_series, attrib)[offset:offset + window+1]))

    avg_array = sum(arrays) / len(arrays)

    gain_array = [0]*avg_array.size
    loss_array = [0]*avg_array.size

    for i, num in reversed(list(enumerate(avg_array))):
        if i == avg_array.size - 1:
            continue
        else:
            change = avg_array[i] - avg_array[i+1]
            if change > 0:
                gain_array[i] = change
            elif change < 0:
                loss_array[i] = -1*change

    avg_gain = np.mean(gain_array)
    avg_loss = np.mean(loss_array)
    rs = avg_gain / avg_loss

    if m.isnan(rs):
        rs = 0
        rsi_value = 0
    else:
        rsi_value = 100 - (100 / (1 + rs))

    if len(gain_array) >= window:
        return rsi_value
    else:
        return None
