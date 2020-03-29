

class Trade:

    num_trades = 0
    all_trades = []

    def __init__(self, asset, quantity, price, timestamp):
        self.asset = asset
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
        Trade.num_trades += 1
        Trade.all_trades.append(self)