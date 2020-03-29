import abc


class Broker(abc.ABC):

    """
    Base class for broker objects.
    Will contain logic for getting order prices
    """

    def __init__(self, name, fee, fee_type, min_order_size=None):
        self.name = name
        self.fee = fee
        self.min_order_size = min_order_size

        assert fee_type == "percentage_of_trade" or fee_type == "absolute_value"
        self.fee_type = fee_type

    def request_order_price(self, time_series_data):
        pass


class InteractiveBrokers(Broker):

    """
    InteractiveBrokers broker class

    """
    def __init__(self):
        super().__init__("Interactive Brokers", 0.0005, "percentage_of_trade", 5)

