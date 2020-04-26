from strategy.strategy import TradingStrategy
from event import events
from random import random


class RandomSignalStrategy(TradingStrategy):

    def __init__(self, name):
        super().__init__(name)

    def generate_signal(self, time_series_data):
        random_signal_generator = random()
        if 0 < random_signal_generator <= 0.4:
            return events.SignalEventBuy(time_series_data["asset"])
        elif 0.4 < random_signal_generator <= 0.8:
            return events.SignalEventSell(time_series_data["asset"])
        else:
            return None
