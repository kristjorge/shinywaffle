from enum import Enum


class OrderSide(str, Enum):
    BUY = 'buy'
    SELL = 'sell'


class OrderType(str, Enum):
    MARKET = 'market'
    LIMIT = 'limit'


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'