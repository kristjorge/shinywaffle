from strategy.strategy import TradingStrategy
from common.event import events
from random import random


class RandomSignalStrategy(TradingStrategy):

    def __init__(self, context):
        super().__init__(context, 'Random testing strategy')

    def trading_logic(self, asset):
        random_signal_generator = random()
        if 0 < random_signal_generator <= 0.05:
            order_volume = self.context.account.risk_manager.calculate_position_volume(asset.ticker)
            return events.SignalEventMarketBuy(asset, order_volume)

        elif 0.05 < random_signal_generator <= 0.1:
            # Selling off entire holding of each asset every time the signal is triggered
            order_volume = self.context.account.assets[asset.ticker]['holding']
            return events.SignalEventMarketSell(asset, order_volume)

        else:
            pass