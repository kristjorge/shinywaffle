import math as m
import numpy.random as rand
from event import events
from utils.misc import round_half_down


class Broker:

    """
    Base class for broker objects.
    Will contain logic for getting order prices

    Modelling slippage as a normal distribution with mean 0 and standard deviation of 0.05

    """

    slippages = abs(rand.normal(0, 0.05, 100000)).tolist()

    def __init__(self, name, fee, min_order_size=None, min_order_currency='USD'):
        self.name = name
        self.fee = fee
        self.min_order_size = min_order_size
        self.min_order_currency = min_order_currency
        self.total_commission = 0

    def fill_buy_order(self, order_event, order_price):
        # Round down
        # TODO: Find a way to round down to the lowest possible unit of the asset
        # Meaning whole stocks for stocks, 1e-8 for crypto and 0.01 for forex
        order_volume = m.floor(order_event.order_size / order_price)
        order_size = order_volume * order_price
        commission = self.calculate_commission(order_size)

        return events.OrderFilledEvent(order_event.asset, order_price, order_size, order_volume, 'buy', commission)

    def fill_sell_order(self, order_event, order_price, max_volume=None):
        # Round down
        # TODO: Find a way to round down to the lowest possible unit of the asset
        # Meaning whole stocks for stocks, 1e-8 for crypto and 0.01 for forex
        if max_volume is None:
            order_volume = m.floor(order_event.order_size / order_price)
            order_volume = round_half_down(order_event.order_size / order_price, order_event.asset.num_decimal_points)
        else:
            order_volume = max_volume

        order_size = order_volume * order_price
        commission = self.calculate_commission(order_size)
        if order_size > 0:
            return events.OrderFilledEvent(order_event.asset, order_price, order_size, order_volume, 'sell', commission)
        else:
            return None

    @staticmethod
    def request_buy_order_price(time_series_data):
        s = Broker.slippages.pop()
        return time_series_data['bars'][0].close + s

    @staticmethod
    def request_sell_order_price(time_series_data):
        s = Broker.slippages.pop()
        return time_series_data['bars'][0].close - s

    def calculate_commission(self, order_size):
        raise NotImplemented

    def self2dict(self):
        data = {
            'name': self.name,
            'fee': self.fee,
            'min order size': self.min_order_size,
            'min order size currency': self.min_order_currency,
            'total commission': self.total_commission
        }

        return data


class InteractiveBrokers(Broker):

    """
    InteractiveBrokers broker class

    """
    def __init__(self):
        super().__init__("Interactive Brokers", 0.0005, 5, 'USD')

    def calculate_commission(self, order_size):
        commission = order_size * self.fee
        self.total_commission += commission
        return commission


class Binance(Broker):
    """
    Binance cryptocurrency exchange / broker class

    """

    def __init__(self):
        super().__init__("Binance", 0.001, 0, 'BTC')

    def calculate_commission(self, order_size):
        commission = order_size * self.fee
        self.total_commission += commission
        return commission
