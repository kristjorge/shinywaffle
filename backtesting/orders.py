from common.event import events


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
        for type, list in self.pending_orders.items():
            for o in list:
                pending_order_events.append(events.PendingOrderEvent(o.id))

        return pending_order_events

    def new_order(self, order):
        order.id = self.latest_id
        self.latest_id += 1
        self.pending_orders[type(order)].append(order)
        return events.PendingOrderEvent(order.id)

    def get_by_id(self, order_id):
        for order_list in self.pending_orders.values():
            order = [o for o in order_list if o.id == order_id]
            try:
                return order[0]
            except IndexError:
                continue

    def fill_order(self, pending_order_id, price, size, commission):
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
                                       self.context.retrieved_data.time)


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
        self.type = 'market'


class LimitOrder:
    def __init__(self, limit_price):
        self.type = 'limit'
        self.order_limit_price = limit_price


class BuyOrder:
    def __init__(self):
        self.side = 'buy'


class SellOrder:
    def __init__(self):
        self.side = 'sell'


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

