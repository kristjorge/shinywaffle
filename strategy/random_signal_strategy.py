from strategy.strategy import TradingStrategy
from common.event import events
from random import random


class RandomSignalStrategy(TradingStrategy):

    def __init__(self, context):
        super().__init__(context, 'Random testing strategy')

    def trading_logic(self, asset):
        random_signal_generator = random()
        if 0 < random_signal_generator <= 0.4:
            order_size = self.context.account.risk_manager.calculate_position_size()
            return events.MarketOrderBuyEvent(asset, order_size)

        elif 0.4 < random_signal_generator <= 0.8:
            max_volume = self.context.account.assets[asset.ticker]['holding']
            order_size = self.context.account.risk_manager.calculate_position_size()
            return events.MarketOrderSellEvent(asset, order_size, max_volume)

        else:
            pass