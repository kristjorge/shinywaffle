
"""
Event base class is used as super for all other classes
Classes for the different types of events
"""


class Event:
    def __init__(self, stock):
        self.stock = stock


class TimeSeriesEvent(Event):
    def __init__(self, stock):
        super().__init__(stock)
        self.event_type = "TIME_SERIES"


class SignalEvent(Event):
    def __init__(self, stock):
        super().__init__(stock)
        self.event_type = "SIGNAL"


class LimitOrderEvent(Event):
    def __init__(self, stock, quantity, price):
        super().__init__(stock)
        self.event_type = "LIMIT_ORDER"
        self.quantity = quantity
        self.price = price


class MarketOrderEvent(Event):
    def __init__(self, stock, quantity):
        super().__init__(stock)
        self.event_type = "MARKET_ORDER"
        self.quantity = quantity


class StopLossEvent(Event):
    def __init__(self, stock, quantity):
        super().__init__(stock)
        self.event_type = "STOP_LOSS"
        self.quantity = quantity


class TrailingStopEvent(Event):
    def __init__(self, stock, quantity):
        super().__init__(stock)
        self.event_type = "TRAILING_STOP"
        self.quantity = quantity
