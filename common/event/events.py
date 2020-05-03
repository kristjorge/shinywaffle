from common.assets import assets


class Event:

    """
    Event base class is used as super for all other classes
    Classes for the different types of events
    """

    def __init__(self, asset):
        assert isinstance(asset, assets.Asset)
        self.asset = asset

    def __str__(self):
        return type(self).__name__


class BuyEvent:
    def __init__(self):
        self.side = 'buy'


class SellEvent:
    def __init__(self):
        self.side = 'sell'


class MarketEvent:
    def __init__(self):
        self.type = 'market'


class LimitEvent:
    def __init__(self, limit_price):
        self.type = 'limit'
        self.order_limit_price = limit_price


class TimeSeriesEvent(Event):
    def __init__(self, asset):
        super().__init__(asset)


class SignalEventMarketBuy(Event, MarketEvent, BuyEvent):
    def __init__(self, asset, order_volume):
        Event.__init__(self, asset)
        MarketEvent.__init__(self)
        BuyEvent.__init__(self)
        self.order_volume = order_volume


class SignalEventLimitBuy(Event, LimitEvent, BuyEvent):
    def __init__(self, asset, order_volume, order_limit_price):
        Event.__init__(self, asset)
        LimitEvent.__init__(self, order_limit_price)
        BuyEvent.__init__(self)
        self.order_volume = order_volume


class SignalEventMarketSell(Event, MarketEvent, SellEvent):
    def __init__(self, asset, order_volume):
        Event.__init__(self, asset)
        MarketEvent.__init__(self)
        SellEvent.__init__(self)
        self.order_volume = order_volume


class SignalEventLimitSell(Event, LimitEvent, SellEvent):
    def __init__(self, asset, order_volume, order_limit_price):
        Event.__init__(self, asset)
        LimitEvent.__init__(self, order_limit_price)
        SellEvent.__init__(self)
        self.order_volume = order_volume


class StopLossEvent(Event):
    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size


class TrailingStopEvent(Event):
    def __init__(self, asset, order_size):
        super().__init__(asset)
        self.order_size = order_size


class PendingOrderEvent:
    def __init__(self, order_id):
        self.order_id = order_id


class OrderFilledEvent(Event):
    def __init__(self, asset, price, size, volume, type, side, commission, time):
        super().__init__(asset)
        self.price = price
        self.order_size = size
        self.type = type        # 'market' or 'limit'
        self.side = side        # 'buy' or 'sell
        self.order_volume = volume
        self.commission = commission
        self.time = time

