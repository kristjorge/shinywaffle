from strategy.strategy import TradingStrategy
from common.event import events


class FixedDatesTransactionsStrategy(TradingStrategy):

    def __init__(self, context):
        super().__init__(context, 'Random testing strategy')

    def trading_logic(self, asset):
        if self.context.retrieved_data.time.day == 15:
            order_volume = self.context.account.risk_manager.calculate_position_volume(asset.ticker)
            return events.SignalEventMarketBuy(asset, order_volume)

        if self.context.retrieved_data.time.day == 1:
            # Selling of entire holding every 1st of each month
            order_volume = self.context.account.assets[asset.ticker]['holding']
            return events.SignalEventMarketSell(asset, order_volume)

        else:
            pass