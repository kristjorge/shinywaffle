

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

    def new_order(self, order):
        order.id = self.latest_id
        self.latest_id += 1
        self.pending_orders[type(order)].append(order)


class Order:
    def __init__(self, asset, volume, type, side, time):
        self.id = None
        self.asset = asset
        self.volume = volume
        self.type = type
        self.side = side
        self.time = time


class MarketBuyOrder(Order):
    def __init__(self, asset, volume, time):
        super().__init__(asset, volume, 'market', 'buy', time)


class MarketSellOrder(Order):
    def __init__(self, asset, volume, time):
        super().__init__(asset, volume, 'market', 'sell', time)


class LimitBuyOrder(Order):
    def __init__(self, asset, volume, limit_price, time):
        super().__init__(asset, volume, 'limit', 'buy', time)
        self.limit_price = limit_price


class LimitSellOrder(Order):
    def __init__(self, asset, volume, limit_price, time):
        super().__init__(asset, volume, 'limit', 'sell', time)
        self.limit_price = limit_price
