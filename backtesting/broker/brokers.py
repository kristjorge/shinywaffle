from abc import ABC


class Broker(ABC):

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


class InteractiveBrokers(Broker):

    """
    InteractiveBrokers broker class

    """
    def __init__(self):
        super().__init__("Interactive Brokers", 0.0005, "percentage_of_trade", 5)
