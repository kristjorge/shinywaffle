

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
