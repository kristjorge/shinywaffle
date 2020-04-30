import pandas as pd
from data.bar import Bar
from data.time_series_data import TimeSeries
from datetime import datetime


class BarProvider:

    def __new__(cls, path: str, date_string_format: str):
        bars = list()
        df = pd.read_csv(path)

        assert 'Open' in df.columns
        assert 'Close' in df.columns
        assert 'High' in df.columns
        assert 'Low' in df.columns
        assert 'Volume' in df.columns
        assert 'Date' in df.columns

        for index, row in df.iterrows():
            bar = Bar(datetime.strptime(row["Date"], date_string_format),
                      row['Open'],
                      row['Close'],
                      row['High'],
                      row['Low'],
                      row['Volume'])
            bars.append(bar)

        bars.sort(key=lambda b: b.time, reverse=True)
        time_series = TimeSeries()
        time_series.set(bars)
        return time_series
