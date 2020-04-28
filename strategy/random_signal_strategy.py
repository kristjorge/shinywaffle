from strategy.strategy import TradingStrategy
from common.event import events
from random import random


class RandomSignalStrategy(TradingStrategy):

    def __init__(self, context):
        super().__init__(context, 'Random testing strategy')

    def generate_signal(self, time_series_data):
        random_signal_generator = random()
        if 0 < random_signal_generator <= 0.4:
            order_size = self.context.account.risk_manager.calculate_position_size()
            return events.MarketOrderBuyEvent(time_series_data["asset"], order_size)
        elif 0.4 < random_signal_generator <= 0.8:
            max_volume = self.context.assets[asset.ticker]['holding']
            return events.MarketOrderSellEvent() (time_series_data["asset"])
        else:
            return None
