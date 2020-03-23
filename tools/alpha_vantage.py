from tools.rest_api import API
from tools.api_link import AlphaVantageLink
from data.bar import BarContainer
from data.bar import Bar
from datetime import datetime
import requests


class AlphaVantage(API):

    """

    Class for interacting with the AlphaVantage REST API
    Currently only usable with historical data


    """

    def __init__(self, token):
        super().__init__(token)
        self.base_url = "https://www.alphavantage.co/query?function="

    def query_stocks(self, function, symbol, return_as_link=False, ascending=False, interval="60min", outputsize="full", use_adjusted_close=False):

        """
        Function to create query string used to get stock data from the VantageAlpha API

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
        opn = '1. open'
        high = '2. high'
        low = '3. low'
        close = '4. close'
        volume = '5. volume'

        assert interval == "1min" \
               or interval == "5min" \
               or interval == "15min" \
               or interval == "30min" \
               or interval == "60min"

        assert outputsize == "compact" \
               or outputsize == "full"

        assert function == "TIME_SERIES_INTRADAY" \
               or function == "TIME_SERIES_DAILY" \
               or function == "TIME_SERIES_DAILY_ADJUSTED"

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

            if use_adjusted_close:
                volume = '6. volume'
                close = '5. adjusted close'

        # If the query is not intended to be returned as a link to the API, return a BarContainer object
        if not return_as_link:
            # Making http request
            response = requests.get(url).json()
            bars = []
            for i in response[json_header]:
                data = response[json_header][i]
                bar = Bar(datetime.strptime(i, datetime_format),
                          data[opn],
                          data[close],
                          data[high],
                          data[low],
                          data[volume])

                bars.append(bar)

            if ascending:
                bars.reverse()

            bar_container = BarContainer(interval)
            bar_container.set(bars)
            response = bar_container
            return response

        # Return as link to the API
        else:
            return AlphaVantageLink(url, json_header, datetime_format, interval, opn, close, high, low, volume, ascending)

    def query_forex(self, function, from_currency, to_currency, return_as_link=False, ascending=False, interval="60min", outputsize="full"):

        """
        Function to create query string used to get forex data from the VantageAlpha API

        function =
            CURENCY_EXCHANGE_RATE for daily Forex exchange rates
            FX_INTRADAY for intraday exchange rates

        From symbol / currency =
            Curreny exchanged from

        To symbol / currency =
            Curreny exchanged to

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

        url = self.base_url

        assert interval == "1min" \
               or interval == "5min" \
               or interval == "15min" \
               or interval == "30min" \
               or interval == "60min"

        assert outputsize == "compact" \
               or outputsize == "full"

        assert function == "CURRENCY_EXCHANGE_RATE" \
               or function == "FX_INTRADAY"

        json_header = ""
        datetime_format = ""

        if function == "CURRENCY_EXCHANGE_RATE":

            url = self.base_url + function \
                  + "&from_currency=" + from_currency \
                  + "&to_currency=" + to_currency \
                  + "&apikey=" + self.token \
                  + "&outputsize=" + outputsize

            json_header = "Time Series FX (Daily)"
            datetime_format = "%Y-%m-%d"
            interval = "daily"
            url = url

        elif function == "FX_INTRADAY":

            url = self.base_url + function \
                  + "&from_symbol=" + from_currency \
                  + "&to_symbol=" + to_currency \
                  + "&interval=" + interval \
                  + "&apikey=" + self.token \
                  + "&outputsize=" + outputsize
            json_header = "Time Series FX (" + interval + ")"
            datetime_format = "%Y-%m-%d %H:%M:%S"

        opn = '1. open'
        close = '4. close'
        high = '2. high'
        low = '3. low'

        if not return_as_link:
            # Making http request
            response = requests.get(url).json()
            bars = []
            for i in response[json_header]:
                data = response[json_header][i]
                bar = Bar(datetime.strptime(i, datetime_format),
                          data[opn],
                          data[close],
                          data[high],
                          data[low],
                          0)  # No volume data for forex on AlphaVantage API

                bars.append(bar)

            if ascending:
                bars.reverse()

            bar_container = BarContainer(interval)
            bar_container.set(bars)
            response = bar_container
            return response
        else:
            return AlphaVantageLink(url, json_header, datetime_format, interval, opn, close, high, low, "volume", ascending)


