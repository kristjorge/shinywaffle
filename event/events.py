
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
        TimeSeriesEvent.num_events += 1


class SignalEventBuy(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        SignalEventBuy.num_events += 1


class SignalEventSell(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        SignalEventSell.num_events += 1


class LimitOrderEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity, price):
        super().__init__(asset)
        self.quantity = quantity
        self.price = price
        LimitOrderEvent.num_events += 1


class MarketOrderEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.quantity = quantity
        MarketOrderEvent.num_events += 1


class StopLossEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.quantity = quantity
        StopLossEvent.num_events += 1


class TrailingStopEvent(Event):
    num_events = 0

    def __init__(self, asset, quantity):
        super().__init__(asset)
        self.quantity = quantity
        TrailingStopEvent.num_events += 1


class OrderFillEvent(Event):
    num_events = 0

    def __init__(self, asset):
        super().__init__(asset)
        OrderFillEvent.num_events += 1
