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

    def __init__(self, asset):
        super().__init__(asset)


class SignalEventBuy(Event):

    def __init__(self, asset):
        super().__init__(asset)


class SignalEventSell(Event):

    def __init__(self, asset):
        super().__init__(asset)


class LimitOrderBuyEvent(Event):

    def __init__(self, asset, order_size, price):
        super().__init__(asset)
        self.order_size = order_size
        self.price = price


class LimitOrderSellEvent(Event):

    def __init__(self, asset, order_size, price, max_volume):
        super().__init__(asset)
        self.order_size = order_size
        self.price = price
        self.max_volume = max_volume


class MarketOrderBuyEvent(Event):

    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size


class MarketOrderSellEvent(Event):

    def __init__(self, asset, order_size, max_volume):
        super().__init__(asset)
        self.order_size = order_size
        self.max_volume = max_volume


class StopLossEvent(Event):

    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size


class TrailingStopEvent(Event):

    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size


class OrderFilledEvent(Event):

    def __init__(self, asset, price, order_size, order_volume, order_type, commission):
        super().__init__(asset)
        self.price = price
        self.order_size = order_size
        self.type = order_type  # buy or sell
        self.order_volume = order_volume
        self.commission = commission

