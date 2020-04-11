from financial_assets import financial_assets


class Event:

    """
    Event base class is used as super for all other classes
    Classes for the different types of events
    """

    def __init__(self, asset):
        assert isinstance(asset, financial_assets.FinancialAsset)
        self.asset = asset

    def __str__(self):
        return type(self).__name__


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


class LimitOrderBuyEvent(Event):
    num_events = 0

    def __init__(self, asset, order_size, price):
        super().__init__(asset)
        self.order_size = order_size
        self.price = price
        LimitOrderBuyEvent.num_events += 1


class LimitOrderSellEvent(Event):
    num_events = 0

    def __init__(self, asset, order_size, price, max_volume):
        super().__init__(asset)
        self.order_size = order_size
        self.price = price
        self.max_volume = max_volume
        LimitOrderSellEvent.num_events += 1


class MarketOrderBuyEvent(Event):
    num_events = 0

    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size
        MarketOrderBuyEvent.num_events += 1


class MarketOrderSellEvent(Event):
    num_events = 0

    def __init__(self, asset, order_size, max_volume):
        super().__init__(asset)
        self.order_size = order_size
        self.max_volume = max_volume
        MarketOrderSellEvent.num_events += 1


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

    def __init__(self, asset, price, order_size, order_volume, order_type, commission):
        super().__init__(asset)
        self.price = price
        self.order_size = order_size
        self.type = order_type  # buy or sell
        self.order_volume = order_volume
        self.commission = commission
        OrderFilledEvent.num_events[self.type] += 1

