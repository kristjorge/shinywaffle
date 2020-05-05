from collections import namedtuple
from datetime import datetime


class TradeLog:

    trade = namedtuple("trade",
                       ['asset', 'trade_size', 'trade_price',
                        'trade_volume', 'trade_type', 'trade_side', 'timestamp', 'commission'])

    def __init__(self):
        self.num_trades = 0
        self.all_trades = []

    def new_trade(self,
                  asset, trade_size: float, trade_price: float, trade_volume: int or float,
                  trade_type: str, side: str, timestamp: datetime, commission: float):

        t = TradeLog.trade(asset, trade_size, trade_price, trade_volume, trade_type, side, timestamp, commission)
        self.num_trades += 1
        self.all_trades.append(t)

    def report(self):
        all_dicts = []
        for i, trade in enumerate(self.all_trades):
            trade_data = {
                'trade number': i,
                'asset': trade.asset.name,
                'type': trade.trade_type,
                'side': trade.trade_side,
                'trade size': trade.trade_size,
                'trade price': trade.trade_price,
                'trade volume': trade.trade_volume,
                'trade commission': trade.commission
            }
            all_dicts.append(trade_data)

        return all_dicts
