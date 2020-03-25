from data.bar import BarContainer
import numpy as np


def simple_moving_average(bars, window, offset=0, ohcl=False):

    """
    Method for calculating the simple moving average for bar time series data.
    :param bars: a BarContainer object with bars
    :param window: lookback windows used to calculate simple moving average (number of periods)
    :param offset: Offsetting the zero index back in time
    :param ohcl: instead of using the close price, the user can opt to use the ohcl average
    :return: a number for the simple moving average
    """

    assert isinstance(bars, BarContainer)
    close_bars = np.array([bars.close[offset:offset + window]])
    if len(close_bars) == window:

        if ohcl:
            open_bars = np.array([bars.open[offset:offset + window]])
            high_bars = np.array([bars.high[offset:offset + window]])
            low_bars = np.array([bars.low[offset:offset + window]])
            average = np.mean((open_bars + close_bars + high_bars + low_bars)/4)
        else:
            average = np.mean(close_bars)

        return average
    else:
        return None

    # if ohcl:
    #     open_bars = np.array([b.open for i, b in enumerate(bars) if
    #                           len(bars) - window - offset < i <= len(bars) - offset])
    #     close_bars = np.array([b.close for i, b in enumerate(bars) if
    #                            len(bars) - window - offset < i <= len(bars) - offset])
    #     high_bars = np.array([b.high for i, b in enumerate(bars) if
    #                           len(bars) - window - offset < i <= len(bars) - offset])
    #     low_bars = np.array([b.low for i, b in enumerate(bars) if
    #                          len(bars) - window - offset < i <= len(bars) - offset])
    #
    #     average = np.mean((open_bars + close_bars + high_bars + low_bars) / 4)
    #
    # else:
    #     close_bars = np.array([b.close for i, b in enumerate(bars) if
    #                            len(bars) - window - offset < i <= len(bars) - offset])
    #     average = np.mean(close_bars)
    #
    # return average


