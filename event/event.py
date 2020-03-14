"""
Super class for events
"""


class Event:
    def __init__(self, stock):
        self.stock = stock


class MarketEvent(Event):
    def __init__(self, stock):
        super().__init__(stock)
        self.event_type = "MARKET"


class SignalEvent(Event):
    def __init__(self, stock):
        super().__init__(stock)
        self.event_type = "SIGNAL"
