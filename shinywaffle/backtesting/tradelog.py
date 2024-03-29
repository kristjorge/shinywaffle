from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from shinywaffle.common.assets import Asset
    from shinywaffle.backtesting import OrderType, OrderSide


class Trade:
    def __init__(self, asset: Asset, size: float, fill_price: float, order_price: float, volume: Union[int, float], time: datetime,
                 commission: float, trade_side: OrderSide, trade_type: OrderType):
        self.asset = asset
        self.size = size
        self.fill_price = fill_price
        self.order_price = order_price
        self.volume = volume
        self.time = time
        self.commission = commission
        self.trade_side = trade_side
        self.trade_type = trade_type

    @property
    def slippage_cost(self) -> float:
        return abs(self.volume * (self.fill_price - self.order_price))


class TradeLog:
    def __init__(self):
        self.num_trades = 0
        self.all_trades = []

    def new_trade(self, asset: Asset, trade_size: float, fill_price: float, order_price: float,
                  trade_volume: Union[int, float], trade_type: OrderType, trade_side: OrderSide, timestamp: datetime,
                  commission: float):

        t = Trade(asset=asset, size=trade_size, fill_price=fill_price, order_price=order_price,
                  volume=trade_volume, time=timestamp, commission=commission, trade_side=trade_side,
                  trade_type=trade_type)

        self.num_trades += 1
        self.all_trades.append(t)

    def report(self):
        all_dicts = []
        for i, trade in enumerate(self.all_trades):
            trade_data = {
                'trade number': i,
                'asset': trade.asset.name,
                'type': trade.trade_type.value,
                'side': trade.trade_side.value,
                'size': trade.size,
                'fill price': trade.fill_price,
                'order price': trade.order_price,
                'slippage cost': trade.slippage_cost,
                'volume': trade.volume,
                'commission': trade.commission
            }
            all_dicts.append(trade_data)

        return all_dicts
