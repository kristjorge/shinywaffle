

def get_datetime_format(interval):
    datetime_format = "%Y-%d-%m"

    if interval == "1min" or interval == "5min" or interval == "15min" or interval == "30min" or interval == "60min":
        datetime_format += " %H:%M:%S"

    return datetime_format
