import numpy as np
from data.time_series_data import DataSeries
from technical_indicators.simple_moving_average import simple_moving_average


def bollinger_bands(data_series, window, attributes, num_stdev=2, offset=0):

    assert isinstance(data_series, DataSeries)
    assert isinstance(attributes, list) or isinstance(attributes, str)

    if type(attributes) != list:
        attributes = [attributes]

    arrays = []
    for attrib in attributes:
        assert hasattr(data_series[0], attrib), "{} is not an attribute in the data series".format(attrib)
        arrays.append(np.array(getattr(data_series, attrib)[offset:offset + window]))

    std_dev = np.std((sum(arrays) / len(arrays)))
    moving_average = simple_moving_average(data_series, window, attributes, offset)

    if arrays[0].size >= window:
        return moving_average + num_stdev * std_dev, moving_average - num_stdev * std_dev
    else:
        return None
