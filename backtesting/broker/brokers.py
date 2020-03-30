import abc
import math as m
from event import events


class Broker(abc.ABC):

    """
    Base class for broker objects.
    Will contain logic for getting order prices
    """

    total_commission = 0

    def __init__(self, name, fee, fee_type, min_order_size=None, min_order_currency='USD'):
        self.name = name
        self.fee = fee
        self.min_order_size = min_order_size
        self.min_order_currency = min_order_currency

        assert fee_type == "percentage_of_trade" or fee_type == "absolute_value"
        self.fee_type = fee_type

    def fill_order(self, order_event, order_price):
        # Round down
        # TODO: Find a way to round down to the lowest possible unit of the asset
        # Meaning whole stocks for stocks, 1e-8 for crypto and 0.01 for forex
        order_volume = m.floor(order_event.order_size / order_price)
        order_size = order_volume * order_price
        commission = self.calculate_commission(order_size)

        return events.OrderFilledEvent(order_event.asset, order_price, order_size, order_volume, order_event.type, commission)

    @staticmethod
    def request_order_price(time_series_data):
        return time_series_data['bars'][0].close

    @abc.abstractmethod
    def calculate_commission(self, order_size):
        pass


class InteractiveBrokers(Broker):

    """
    InteractiveBrokers broker class

    """
    def __init__(self):
        super().__init__("Interactive Brokers", 0.0005, "percentage_of_trade", 5, 'USD')

    def calculate_commission(self, order_size):
        total_trade_value = order_size
        commission = total_trade_value * self.fee
        InteractiveBrokers.total_commission += commission
        return commission
