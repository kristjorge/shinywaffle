from shinywaffle.common.event import events
from shinywaffle.common.event.events import PendingOrderEvent
from shinywaffle.backtesting import OrderSide, OrderType
from typing import Union


class Order:
    def __init__(self, asset, volume, time):
        self.id = None
        self.asset = asset
        self.volume = volume
        self.time = time
        self.filled_price = None
        self.size = None
        self.commission = None
        self.expires_at = expires_at


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
        pending_order_events = []
        for order_list in self.pending_orders.values():
            for order in order_list:
                if order.expires_at is None:
                    pending_order_events.append(events.PendingOrderEvent(order.id))
                else:
                    if order.expires_at <= self.context.time:
                        pending_order_events.append(events.PendingOrderEvent(order.id, expires_at=order.expires_at))
                    else:
                        self.cancelled_orders[type(order)].append(order)

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

    def fill_order(self, pending_order_id: int, price: float, size: Union[int, float], commission: float):
        """
        Fills a pending order

        Returns a OrderFilledEvent
        """
        order = self.get_by_id(pending_order_id)
        order.filled_price = price
        order.size = size
        order.commission = commission

        for idx, o in enumerate(self.pending_orders[type(order)]):
            if o.id == pending_order_id:
                filled_order = self.pending_orders[type(order)].pop(idx)
                self.filled_orders[type(order)].append(filled_order)
                break

        return events.OrderFilledEvent(order.asset,
                                       order.filled_price,
                                       order.size,
                                       order.volume,
                                       order.type,
                                       order.side,
                                       order.commission,
                                       self.context.time)
