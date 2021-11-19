from shinywaffle.tools.rest_api import API
from shinywaffle.tools.api_link import BinancePublicLink
from shinywaffle.data.bar import Bar
from shinywaffle.data.time_series_data import TimeSeries, TimeSeriesType
from datetime import datetime
from shinywaffle.utils.misc import datetime_to_epoch
from shinywaffle.utils.misc import epoch_to_datetime
from shinywaffle.utils.misc import query_string
import requests
import math as m


class BinancePublic(API):

    """
    Class for interacting with Binance API for cryptocurrency

    """
    @staticmethod
    def get_interval_milliseconds(interval: str):
        interval_1m = 60*1000
        interval_1h = 60 * interval_1m
        interval_1d = 24 * interval_1h
        if interval == '1m':
            return interval_1m
        elif interval == '3m':
            return 3 * interval_1m
        elif interval == '5m':
            return 5 * interval_1m
        elif interval == '15m':
            return 15 * interval_1m
        elif interval == '30m':
            return 30 * interval_1m
        elif interval == '1h':
            return interval_1h
        elif interval == '2h':
            return 2 * interval_1h
        elif interval == '4h':
            return 4 * interval_1h
        elif interval == '6h':
            return 6 * interval_1h
        elif interval == '8h':
            return 8 * interval_1h
        elif interval == '12h':
            return 12 * interval_1h
        elif interval == '1d':
            return interval_1d
        elif interval == '3d':
            return 3 * interval_1d
        elif interval == '1w':
            return 7 * interval_1d
        elif interval == '1M':
            return 31 * interval_1d

    intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

    def __init__(self, token=None):
        super().__init__(token)
        self.base_url = 'https://api.binance.com'

    def get_candlesticks(self, base_asset: str, quote_asset: str, interval: str, limit: int = 500,
                         time_to: datetime = datetime.now(), time_from: datetime = None, return_as_link: bool = False):

        param_dict = {
            'symbol': quote_asset + base_asset,
            'interval': interval
        }

        end_time = int(datetime_to_epoch(time_to, ms=True))
        final_end_time_ms = end_time
        interval_ms = self.get_interval_milliseconds(interval)
        url = self.base_url + '/api/v3/klines?'
        url = query_string(url, param_dict)

        if not return_as_link:
            response = []
            if time_from is not None:
                start_time = int(datetime_to_epoch(time_from, ms=True))
                num_calls = m.ceil(((end_time - start_time) / interval_ms) / limit)

                for i in range(num_calls):
                    if i == num_calls-1:
                        num_candles = m.floor((final_end_time_ms - start_time) / interval_ms)
                    else:
                        num_candles = limit

                    param_dict = {
                        'endTime': str(int(start_time + (num_candles - 1) * interval_ms)),
                        'startTime': str(start_time),
                        'limit': str(num_candles)
                    }

                    query_url = query_string(url, param_dict)
                    response += self.query(query_url)
                    start_time += limit * interval_ms
            else:
                param_dict = {
                    'endTime': str(end_time),
                    'limit': str(limit)
                }
                query_url = query_string(url, param_dict)
                response += self.query(query_url)

            response.reverse()
            bar_container = TimeSeries()
            bar_container.set(response)
            return bar_container
        else:
            return BinancePublicLink(url, interval)

    @staticmethod
    def query(string):
        """
        Performs a request get call on the supplied URL. Parses the result as a json dictionary and returns the data
        as a list of Bar objects
        :param string: URL
        :return: list of Bar objects
        """
        response = requests.get(string).json()
        bars = []
        for candle in response:
            bar = Bar(epoch_to_datetime(candle[0], ms=True),
                      float(candle[1]),
                      float(candle[4]),
                      float(candle[2]),
                      float(candle[3]),
                      float(candle[5]))
            bars.append(bar)
        return bars
