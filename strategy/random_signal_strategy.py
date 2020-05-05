from strategy.strategy import TradingStrategy
from common.event import events


class FixedDatesTransactionsStrategy(TradingStrategy):

    def __init__(self, context):
        super().__init__(context, 'Random testing strategy')

    def trading_logic(self, asset):
        if self.context.retrieved_data.time.day == 15:
            order_volume = self.context.account.risk_manager.calculate_position_volume(asset.ticker)
            limit_price = self.context.retrieved_data[asset.ticker]['bars'][0].close*0.975
            return events.SignalEventLimitBuy(asset, order_volume, limit_price)
            # return events.SignalEventMarketBuy(asset, order_volume)

        if self.context.retrieved_data.time.day == 1:
            # Selling of entire holding every 1st of each month at market
            order_volume = self.context.account.assets[asset.ticker]['holding']
            return events.SignalEventMarketSell(asset, order_volume)

        else:
            pass
