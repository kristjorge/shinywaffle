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
    def __init__(self, asset, volume, time):
        Order.__init__(self, asset, volume, time)
        MarketOrder.__init__(self)
        BuyOrder.__init__(self)


class MarketSellOrder(Order, MarketOrder, SellOrder):
    def __init__(self, asset, volume, time):
        Order.__init__(self, asset, volume, time)
        MarketOrder.__init__(self)
        SellOrder.__init__(self)


class LimitBuyOrder(Order, LimitOrder, BuyOrder):
    def __init__(self, asset, volume, limit_price, time):
        Order.__init__(self, asset, volume, time)
        LimitOrder.__init__(self, limit_price)
        BuyOrder.__init__(self)


class LimitSellOrder(Order, LimitOrder, SellOrder):
    def __init__(self, asset, volume, limit_price, time):
        Order.__init__(self, asset, volume, time)
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

    def update_post_event_stack(self):
        pending_order_events = []
        for order_list in self.pending_orders.values():
            for order in order_list:
                pending_order_events.append(events.PendingOrderEvent(order.id))

        return pending_order_events

    def new_order(self, order: Union[MarketBuyOrder, MarketSellOrder, LimitBuyOrder, LimitSellOrder]) -> PendingOrderEvent:
        """ Places a new order. Assigns the order id to the latest Id +1. Saves the order in the pending events
        list.
        Returns a PendingOrderEvent object
        """
        order.id = self.latest_id + 1
        self.latest_id = order.id
        self.pending_orders[type(order)].append(order)
        return events.PendingOrderEvent(order.id)

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
