from financial_assets import financial_assets

"""
Event base class is used as super for all other classes
Classes for the different types of events
"""


class Event:
    def __init__(self, asset):
        assert isinstance(asset, financial_assets.FinancialAsset)
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
    num_events = {'buy': 0, 'sell': 0}

    def __init__(self, asset, order_size, price, order_type):
        super().__init__(asset)
        self.order_size = order_size
        self.price = price
        self.type = order_type
        LimitOrderEvent.num_events[self.type]  += 1


class MarketOrderEvent(Event):
    num_events = {'buy': 0, 'sell': 0}

    def __init__(self, asset, order_size, order_type):
        super().__init__(asset)
        self.order_size = order_size
        self.type = order_type
        MarketOrderEvent.num_events[self.type] += 1


class StopLossEvent(Event):
    num_events = 0

    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size
        StopLossEvent.num_events += 1


class TrailingStopEvent(Event):
    num_events = 0

    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size
        TrailingStopEvent.num_events += 1


class OrderFilledEvent(Event):
    num_events = {'buy': 0, 'sell': 0}

    def __init__(self, asset, price, order_size, order_type):
        super().__init__(asset)
        self.price = price
        self.order_size = order_size
        self.type = order_type  # buy or sell
        OrderFilledEvent.num_events[self.type] += 1
