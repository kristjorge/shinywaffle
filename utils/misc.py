from datetime import datetime
import re



def get_datetime_format(interval):
    datetime_format = "%Y-%d-%m"

    if interval == "1min" or interval == "5min" or interval == "15min" or interval == "30min" or interval == "60min":
        datetime_format += " %H:%M:%S"

    return datetime_format


def get_weekday(day_int):
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


def get_backtest_dt(interval):
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


def datetime_to_epoch(timestamp, ms=False):

    total_seconds = timestamp.timestamp()
    if ms:
        return total_seconds * 1000
    else:
        return total_seconds


def epoch_to_datetime(timestamp, ms=False):
    if ms:
        timestamp = timestamp / 1000

    return datetime.fromtimestamp(timestamp)


def query_string(base_url, param_dict):

    for key, value in param_dict.items():
        base_url += '&{}='.format(key) + value

    return base_url
