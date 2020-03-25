
"""
Event base class is used as super for all other classes
Classes for the different types of events
"""


class Event:
    def __init__(self, asset):
        self.asset = asset


class TimeSeriesEvent(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        self.event_type = "TIME_SERIES"
        TimeSeriesEvent.num_events += 1


class SignalEventBuy(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        self.event_type = "SIGNAL BUY"
        SignalEventBuy.num_events += 1


class SignalEventSell(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        self.event_type = "SIGNAL SELL"
        SignalEventSell.num_events += 1


class LimitOrderEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity, price):
        super().__init__(asset)
        self.event_type = "LIMIT_ORDER"
        self.quantity = quantity
        self.price = price
        LimitOrderEvent.num_events += 1


class MarketOrderEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.event_type = "MARKET_ORDER"
        self.quantity = quantity
        MarketOrderEvent.num_events += 1


class StopLossEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.event_type = "STOP_LOSS"
        self.quantity = quantity
        StopLossEvent.num_events += 1


class TrailingStopEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.event_type = "TRAILING_STOP"
        self.quantity = quantity
        TrailingStopEvent.num_events += 1


class OrderFillEvent(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        OrderFillEvent.num_events += 1