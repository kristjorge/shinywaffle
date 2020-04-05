from collections import namedtuple


class TradeLog:

    def __init__(self):
        self.num_trades = 0
        self.active_trades = 0
        self.all_trades = []

    def new_trade(self, asset, trade_size, trade_price, trade_volume, trade_type, timestamp, commission):
        trade = namedtuple("trade",
                           ['asset', 'trade_size', 'trade_price',
                            'trade_volume', 'trade_type', 'timestamp', 'commission'])

        t = trade(asset, trade_size, trade_price, trade_volume, trade_type, timestamp, commission)
        self.num_trades += 1
        self.all_trades.append(t)
        if trade_type == "buy":
            self.active_trades += 1
        elif trade_type == "sell":
            self.active_trades -= 1

    def self2dict(self):
        all_dicts = []
        for i, trade in enumerate(self.all_trades):
            trade_data = {
                'trade number': i,
                'asset': trade.asset.name,
                'type': trade.trade_type,
                'trade size': trade.trade_size,
                'trade price': trade.trade_price,
                'trade volume': trade.trade_volume,
                'trade commission': trade.commission
            }
            all_dicts.append(trade_data)

        return all_dicts
