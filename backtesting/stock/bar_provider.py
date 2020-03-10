import pandas as pd
from utils.bar import Bar
from datetime import datetime
from utils.bar import BarHolder

"""
Providing historical data for stocks

Methods accepted are

    - CSV file
    - API calls to AlphaVantage
    - API calls to
"""

available_methods = ("CSV",
                     "API")

available_apis = ("AlphaVantage",
                  "IEX Cloud")


class BarProvider:

    def __init__(self, method, *arguments):

        """

        :param method: Method describing how the data is provided (CSV or API)
        :param arguments: Arguments handled by the appropriate method of choice

            If method is CSV, then it asserts that only one argument was provided and that
            it is a string. The string is the path to the CSV file holding the price data

            Ìf method is API, the it asserts that there are _two_ arguments provided and that
            those are 1) the name of the API called (currently only AlphaVantage) and

        """

        assert isinstance(method, str)
        assert method in available_methods

        self.bars = None
        self.method = method

        if method == "CSV":
            assert len(arguments) == 1  # Only one additional argument provided
            assert isinstance(arguments[0], str)
            self.interpret_csv(arguments[0])

    def interpret_csv(self, path):
        bars = list()
        df = pd.read_csv(path)

        assert "Open" in df.columns
        assert "Close" in df.columns
        assert "High" in df.columns
        assert "Low" in df.columns
        assert "Volume" in df.columns

        for index, row in df.iterrows():
            bar = Bar(datetime.strptime(row["DateTime"], "%Y-%m-%d"),
                      row["Open"],
                      row["Close"],
                      row["High"],
                      row["Low"],
                      row["Volume"])
            bars.append(bar)

        self.bars = BarHolder(bars)

    def get_bars(self):
        return self.bars

    def get_from_api(self):
        pass
