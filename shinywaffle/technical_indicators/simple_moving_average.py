from __future__ import annotations
from shinywaffle.technical_indicators import TooSmallWindowException
import numpy as np
from typing import TYPE_CHECKING, Union, List

if TYPE_CHECKING:
    from shinywaffle.data.time_series_data import TimeSeries


def simple_moving_average(time_series: TimeSeries, window: int, attributes: Union[str, List[str]], offset: int = 0):

    """
    :param time_series: A TimeSeries object with the data in it
    :param window: the look back window for computing the moving average
    :param offset: the offset of the start of the window
    :param attributes: list of data attributes that that moving average is calculated from
    :return: the moving average as a float

    Raises: TooSmallWindowException if the length of the time series is less than the window length
    """

    if not isinstance(attributes, list):
        attributes = [attributes]

    arrays = []
    for attrib in attributes:
        assert hasattr(time_series[0], attrib), "{} is not an attribute in the data series".format(attrib)
        arrays.append(np.array(getattr(time_series, attrib)[offset:offset + window]))

    avg_array = sum(arrays) / len(arrays)
    moving_average = np.mean(avg_array)
    if arrays[0].size >= window:
        return moving_average
    else:
        raise TooSmallWindowException

