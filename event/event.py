
"""
Event base class is used as super for all other classes
Classes for the different types of events
"""


class Event:
    def __init__(self, asset):
        self.asset = asset


class TimeSeriesEvent(Event):
    def __init__(self, asset):
        super().__init__(asset)
        self.event_type = "TIME_SERIES"


class SignalEventBuy(Event):
    def __init__(self, asset):
        super().__init__(asset)
        self.event_type = "SIGNAL BUY"


class SignalEventSell(Event):
    def __init__(self, asset):
        super().__init__(asset)
        self.event_type = "SIGNAL SELL"


class LimitOrderEvent(Event):
    def __init__(self, asset, quantity, price):
        super().__init__(asset)
        self.event_type = "LIMIT_ORDER"
        self.quantity = quantity
        self.price = price


class MarketOrderEvent(Event):
    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.event_type = "MARKET_ORDER"
        self.quantity = quantity


class StopLossEvent(Event):
    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.event_type = "STOP_LOSS"
        self.quantity = quantity


class TrailingStopEvent(Event):
    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.event_type = "TRAILING_STOP"
        self.quantity = quantity
