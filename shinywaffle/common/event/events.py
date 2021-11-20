from shinywaffle.common import assets
from abc import ABC
from shinywaffle.backtesting import OrderType, OrderSide
from datetime import datetime
from typing import Optional


class Event(ABC):

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
    def __init__(self, expires_at: datetime):
        self.side = OrderSide.BUY
        self.expires_at = expires_at


class SellEvent:
    def __init__(self, expires_at: datetime):
        self.side = OrderSide.SELL
        self.expires_at = expires_at


class MarketEvent:
    def __init__(self):
        self.type = OrderType.MARKET


class LimitEvent:
    def __init__(self, limit_price):
        self.type = OrderType.LIMIT
        self.order_limit_price = limit_price


class TimeSeriesEvent(Event):
    def __init__(self, asset):
        super().__init__(asset)


class SignalEventMarketBuy(Event, MarketEvent, BuyEvent):
    def __init__(self, asset, order_volume, expires_at: Optional[datetime] = None):
        Event.__init__(self, asset)
        MarketEvent.__init__(self)
        BuyEvent.__init__(self, expires_at=expires_at)
        self.order_volume = order_volume


class SignalEventLimitBuy(Event, LimitEvent, BuyEvent):
    def __init__(self, asset, order_volume, order_limit_price, expires_at: Optional[datetime] = None):
        Event.__init__(self, asset)
        LimitEvent.__init__(self, order_limit_price)
        BuyEvent.__init__(self, expires_at=expires_at)
        self.order_volume = order_volume


class SignalEventMarketSell(Event, MarketEvent, SellEvent):
    def __init__(self, asset, order_volume, expires_at: Optional[datetime] = None):
        Event.__init__(self, asset)
        MarketEvent.__init__(self)
        SellEvent.__init__(self, expires_at=expires_at)
        self.order_volume = order_volume


class SignalEventLimitSell(Event, LimitEvent, SellEvent):
    def __init__(self, asset, order_volume, order_limit_price, expires_at: Optional[datetime] = None):
        Event.__init__(self, asset)
        LimitEvent.__init__(self, order_limit_price)
        SellEvent.__init__(self, expires_at=expires_at)
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
    def __init__(self, order_id: int, expires_at: Optional[datetime] = None):
        self.order_id = order_id
        self.expires_at = expires_at


class OrderFilledEvent(Event):
    def __init__(self, asset, price, size, volume, order_type, side, commission, time):
        super().__init__(asset)
        self.price = price
        self.order_size = size
        self.type = order_type
        self.side = side
        self.order_volume = volume
        self.commission = commission
        self.time = time

