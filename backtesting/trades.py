

class Trades:

    num_trades = 0
    all_trades = []

    def __init__(self, asset, trade_size, trade_price, trade_volume, trade_type):
        self.asset = asset
        self.trade_size = trade_size
        self.trade_price = trade_price
        self.trade_volume = trade_volume
        self.trade_type = trade_type
        Trades.num_trades += 1
        Trades.all_trades.append(self)

    @classmethod
    def self2dict(cls):
        all_dicts = []
        for i, trade in enumerate(Trades.all_trades):
            trade_data = {
                'trade number': i,
                'asset': trade.asset.ticker,
                'type': trade.trade_type,
                'trade size': trade.trade_size,
                'trade price': trade.trade_price,
                'trade volume': trade.trade_volume
            }
            all_dicts.append(trade_data)

        return all_dicts
