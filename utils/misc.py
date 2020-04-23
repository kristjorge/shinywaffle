from datetime import datetime
import math

daily_datetime_format = "%Y-%m-%d"


def get_datetime_format(interval: str) -> str:
    """
    Base datetime format is "%Y-%d-%m". If the supplied interval is on an intraday level, append " %H:%M:%S" to it
    :param interval: Interval as a string
    :return: Returns a string with the datetime format used in datetime.strftime() method to output a readable string
    """

    datetime_format = daily_datetime_format

    if interval == "1min" or interval == "5min" or interval == "15min" or interval == "30min" or interval == "60min":
        datetime_format += " %H:%M:%S"

    return datetime_format


def get_weekday(day_int: int) -> str:
    """
    A method that takes an integer representing the number of day in the week and returns the correct string for
    that day.

    Example:
        get_weekday(3) returns thursday
        get_weekday(6) returns sunday

    :param day_int: integer representing day of the week
    :return: string with the name of the day of the week
    """
    if day_int == 0:
        return "monday"
    elif day_int == 1:
        return "tuesday"
    elif day_int == 2:
        return "wednesday"
    elif day_int == 3:
        return "thursday"
    elif day_int == 4:
        return "friday"
    elif day_int == 5:
        return "saturday"
    elif day_int == 6:
        return "sunday"
    else:
        return "N/A"


def get_backtest_dt(interval: str) -> float:
    """
    Method that calculates the time increment used in a backtest setting from the provided interval specified
    in the backtester object

    :param interval: string with the time interval used in the backtesting
    :return: float with the time increment (dt)
    """

    if interval == 'weekly' or interval == '1w':
        dt = 7
    elif interval == "daily" or interval == '1d':
        dt = 1
    elif interval == '12h':
        dt = 12 / 24
    elif interval == '8h':
        dt = 8 / 24
    elif interval == '6h':
        dt = 6 / 24
    elif interval == '4h':
        dt = 4 / 24
    elif interval == '2h':
        dt = 1 / 12
    elif interval == '60min' or interval == '60m':
        dt = 1 / 24
    elif interval == '30min' or interval == '30m':
        dt = 1 / (24*2)
    elif interval == '15min' or interval == '15m':
        dt = 1 / (24*2*2)
    elif interval == '5min' or interval == '5m':
        dt = 1 / (24*2*2*3)
    elif interval == '3min' or interval == '3m':
        dt = 3 / (24*2*2*3*5)
    elif interval == '1min' or interval == '1m':
        dt = 1 / (24*2*2*3*5)
    else:
        dt = 1

    return dt


def datetime_to_epoch(timestamp: datetime, ms: bool = False) -> int:
    """

    Method that returns the time in seconds or milli seconds from epoch from a given datetime timestamp

    :param timestamp: datetime object with the timestamp
    :param ms: bool that decides whether or not the output should be in seconds or milli seconds
    :return: integer with the epoch time
    """

    total_seconds = timestamp.timestamp()
    if ms:
        return int(total_seconds * 1000)
    else:
        return int(total_seconds)


def epoch_to_datetime(timestamp: int, ms: bool = False) -> datetime:

    """
    Method that converts a timestamp in seconds or milli seconds from epoch to a datetime format object
    :param timestamp: seconds or milliseconds from epoch time
    :param ms: bool to decide between seconds or milliseconds
    :return: datetime object
    """

    if ms:
        timestamp = timestamp / 1000

    return datetime.fromtimestamp(timestamp)


def query_string(base_url: str, params: dict) -> str:
    """
    Method that takes a base url and assembles query parameters from a params dict
    :param base_url: base url string containing url to API endpoint
    :param params: key value pair of parameters submitted into the query url
    :return:
    """

    for key, value in params.items():
        base_url += '&{}='.format(key) + value

    return base_url


def round_down(number: float, decimals: int = 0) -> float:
    """
    Method that rounds down based on number of decimal places specified in the arguments
    :param number: number to be rounded down
    :param decimals: number of decimal points
    :return: returns a float with the rounded down applied
    """
    multiplier = 10 ** decimals
    return math.floor(number * multiplier) / multiplier
