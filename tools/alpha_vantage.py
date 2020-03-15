from tools.rest_api import API
from utils.time_series_data import TimeSeriesDataObject
from utils.bar import BarHolder
import requests

"""

Class for interacting with the AlphaVantage REST API
Currently only usable with historical data


"""


class AlphaVantage(API):

    def __init__(self, token):
        super().__init__(token)
        self.base_url = "https://www.alphavantage.co/query?function="

    def query(self, function, symbol, output_as_bars=False, reverse=False, **kwargs):
        """

        Function to create query string used to get data from the VantageAlpha API

        function =
            TIME_SERIES_INTRADAY for intraday data
            TIME_SERIES_DAILY for daily data

        symbol =
            stock symbol

        output_as_bars =
            Set bars=True if the output should a barcontainer with bars
            If bars=False, the request is returned as a json object

        reverse =
            If set to true, the output bars will be reverse
            Only used if output_as_bars = True

        kwargs:  - interval
                        For intraday data. Intervals are "1min", "5min", "15min", "30min" or "60min". Type: String

                - outputsize
                        Determines the number of points returned by the query. Either "full" or "compact". Type: String


        """

        # Getting kwargs
        interval = kwargs.get("interval", "60min")
        outputsize = kwargs.get("outputsize", "full")

        assert interval == "1min" or interval == "5min" or interval == "15min" or interval == "30min" or interval == "60min"
        assert outputsize == "compact" or outputsize == "full"

        url = self.base_url + function \
              + "&symbol=" + symbol \
              + "&apikey=" + self.token \
              + "&outputsize=" + outputsize

        json_header = ""
        datetime_format = ""

        if function == "TIME_SERIES_INTRADAY":
            json_header = "Time Series (" + interval + ")"
            datetime_format = "%Y-%m-%d %H:%M:%S"
            url = url + "&interval=" + interval

        elif function == "TIME_SERIES_DAILY":
            json_header = "Time Series (Daily)"
            datetime_format = "%Y-%m-%d"
            interval = "daily"
            url = url

        elif function == "TIME_SERIES_DAILY_ADJUSTED":
            json_header = "Time Series (Daily)"
            datetime_format = "%Y-%m-%d"
            interval = "daily"
            url = url

        # Making http request
        response = requests.get(url).json()
        if output_as_bars:
            bars = []
            for i in response[json_header]:
                data = response[json_header][i]
                #bar = Bar(datetime.strptime(i, datetime_format),
                #          data['1. open'],
                #          data['4. close'],
                #          data['2. high'],
                #          data['3. low'],
                #          data['5. volume'])

                # Removing the prefix 1., 2., etc with dict comprehension
                new_data = {key[3:]: value for key, value in data.items()}
                new_data["datetime"] = i
                bar = TimeSeriesDataObject(new_data, datetime_format)
                bars.append(bar)

            if reverse:
                # Reversing the list of bars since since API from new to old
                bars.reverse()
            response = BarHolder(bars, interval)
        return response
