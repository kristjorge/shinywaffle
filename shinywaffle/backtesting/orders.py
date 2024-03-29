from __future__ import annotations
from datetime import datetime
from shinywaffle.common.event import events
from shinywaffle.common.event.events import PendingOrderEvent
from shinywaffle.backtesting import OrderSide, OrderType
from typing import Union, TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from shinywaffle.common.assets import Asset


class EmptyOrderError(Exception):
    def __init__(self):
        """ Exception raised when trying to sell off a position for an asset does not have a balance """
        super().__init__()


class Order:
    def __init__(self, asset: Asset, volume: Union[int, float], time: datetime, expires_at: datetime):
        self.id = None
        self.asset = asset
        self.volume = volume
        self.time = time
        self.order_price = None
        self.filled_price = None
        self.size = None
        self.commission = None
        self.expires_at = expires_at

        if self.volume == 0:
            raise EmptyOrderError

    @property
    def slippage_cost(self) -> float:
        return abs((self.filled_price-self.order_price) * self.volume)


class MarketOrder:
    def __init__(self):
        self.type = OrderType.MARKET


class LimitOrder:
    def __init__(self, limit_price):
        self.type = OrderType.LIMIT
        self.order_limit_price = limit_price


class BuyOrder:
    def __init__(self):
        self.side = OrderSide.BUY


class SellOrder:
    def __init__(self):
        self.side = OrderSide.SELL


class MarketBuyOrder(Order, MarketOrder, BuyOrder):
    def __init__(self, asset: Asset, volume: Union[int, float], time: datetime, expires_at: Optional[datetime] = None):
        Order.__init__(self, asset, volume, time, expires_at=expires_at)
        MarketOrder.__init__(self)
        BuyOrder.__init__(self)


class MarketSellOrder(Order, MarketOrder, SellOrder):
    def __init__(self, asset: Asset, volume: Union[int, float], time: datetime, expires_at: Optional[datetime] = None):
        Order.__init__(self, asset, volume, time, expires_at=expires_at)
        MarketOrder.__init__(self)
        SellOrder.__init__(self)


class LimitBuyOrder(Order, LimitOrder, BuyOrder):
    def __init__(self, asset: Asset, volume: Union[int, float], limit_price: float, time: datetime,
                 expires_at: Optional[datetime] = None):
        Order.__init__(self, asset, volume, time, expires_at=expires_at)
        LimitOrder.__init__(self, limit_price)
        BuyOrder.__init__(self)


class LimitSellOrder(Order, LimitOrder, SellOrder):
    def __init__(self, asset: Asset, volume: Union[int, float], limit_price: float, time: datetime,
                 expires_at: Optional[datetime] = None):
        Order.__init__(self, asset, volume, time, expires_at=expires_at)
        LimitOrder.__init__(self, limit_price)
        SellOrder.__init__(self)


ANY_ORDER_TYPE = Union[MarketBuyOrder, MarketSellOrder, LimitBuyOrder, LimitSellOrder]


class OrderBook:

    def __init__(self, context):
        self.context = context
        self.latest_id = 0
        self.pending_orders = {
            MarketBuyOrder: [],
            LimitBuyOrder: [],
            MarketSellOrder: [],
            LimitSellOrder: []
        }

        self.filled_orders = {
            MarketBuyOrder: [],
            LimitBuyOrder: [],
            MarketSellOrder: [],
            LimitSellOrder: []
        }

        self.cancelled_orders = {
            MarketBuyOrder: [],
            LimitBuyOrder: [],
            MarketSellOrder: [],
            LimitSellOrder: []
        }

    def update_post_event_stack(self) -> List[PendingOrderEvent]:
        """
        Updates the post event stack in the event handler with a list of pending events.

        If the PendingOrderEvent does not have an expire date, then add it to the list of pending events
        If the PendingOrderEvent has an expire date, but it's not been reached yet then also add it to the list of
        pending events
        However, it the PendingOrderEvent has expired, then do not add it to the list of pending events, but rather
        to the list of cancelled even

        """
        pending_order_events = list()
        order_ids_to_cancel = list()
        for order_list in self.pending_orders.values():
            for order in order_list:
                if order.expires_at is None:
                    # Order is still active
                    pending_order_events.append(events.PendingOrderEvent(order.id, expires_at=order.expires_at))
                else:
                    if order.expires_at <= self.context.time:
                        # Order is still active
                        pending_order_events.append(events.PendingOrderEvent(order.id, expires_at=order.expires_at))
                    else:
                        # Order has expired
                        order_ids_to_cancel.append(order.id)

        # For all ids in the list of cancelled order ids
        # Get the order object and find the index of the order object in the pending orders list
        # Then pop that order and put it in the cancelled orders
        for order_id in order_ids_to_cancel:
            order = self.get_by_id(order_id=order_id)
            for ind, pending_order in enumerate(self.pending_orders[type(order)]):
                if pending_order.id == order_id:
                    cancelled_order = self.pending_orders[type(order)].pop(ind)
                    self.cancelled_orders[type(order)].append(cancelled_order)

        return pending_order_events

    def new_order(self, order: Union[MarketBuyOrder, MarketSellOrder, LimitBuyOrder, LimitSellOrder]) -> PendingOrderEvent:
        """ Places a new order. Assigns the order id to the latest Id +1. Saves the order in the pending events
        list.
        Returns a PendingOrderEvent object
        """
        order.id = self.latest_id + 1
        self.latest_id = order.id
        self.pending_orders[type(order)].append(order)
        return events.PendingOrderEvent(order_id=order.id, expires_at=order.expires_at)

    def get_by_id(self, order_id: int) -> Union[MarketBuyOrder, MarketSellOrder, LimitBuyOrder, LimitSellOrder]:
        """ Gets an order by the ID"""
        for order_list in self.pending_orders.values():
            order = [o for o in order_list if o.id == order_id]
            try:
                return order[0]
            except IndexError:
                continue

    def fill_order(self, pending_order_id: int, filled_price: float, order_price: float, size: Union[int, float],
                   commission: float) -> events.OrderFilledEvent:
        """
        Fills a pending order

        Returns a OrderFilledEvent
        """
        order = self.get_by_id(pending_order_id)
        order.filled_price = filled_price
        order.order_price = order_price
        order.size = size
        order.commission = commission

        for idx, o in enumerate(self.pending_orders[type(order)]):
            if o.id == pending_order_id:
                filled_order = self.pending_orders[type(order)].pop(idx)
                self.filled_orders[type(order)].append(filled_order)
                break

        return events.OrderFilledEvent(asset=order.asset,
                                       filled_price=order.filled_price,
                                       order_price=order.order_price,
                                       size=order.size,
                                       volume=order.volume,
                                       order_type=order.type,
                                       side=order.side,
                                       commission=order.commission,
                                       time=self.context.time)

    def report(self) -> dict:
        return {
            'pending_order': {key.__name__: len(values) for key, values in self.pending_orders.items()},
            'filled_orders': {key.__name__: len(values) for key, values in self.filled_orders.items()},
            'cancelled_orders': {key.__name__: len(values) for key, values in self.cancelled_orders.items()}
        }