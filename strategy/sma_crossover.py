from strategy.strategy import TradingStrategy
from common.event import events
from technical_indicators.simple_moving_average import simple_moving_average
from technical_indicators import TooSmallWindowException


class AverageCrossOver(TradingStrategy):

    """
    Sample code for a simple SMA crossover strategy.
    If the short SMA crosses above the long SMA,
    """

    def __init__(self, context, short, long):
        super().__init__(context, 'Simple moving average crossover')
        self.short = short
        self.long = long

    def trading_logic(self, asset):

        """
        :param asset: Asset that have generated a market signal in the event handler
        :return: Either a SignalEventBuy or SignalEventSell based on the signal generated by the logic in this method

        For now only returning a buy signal as I have yet to implement any technical indicators
        """

        bars = self.context.retrieved_data[asset.ticker]['bars']

        try:
            short_current = simple_moving_average(bars, self.short, ["close", "high", "low"], offset=0)
            short_previous = simple_moving_average(bars, self.short, ["close", "high", "low"], offset=1)

            long_current = simple_moving_average(bars, self.long, ["close", "high", "low"], offset=0)
            long_previous = simple_moving_average(bars, self.long, ["close", "high", "low"], offset=1)

            if short_current > long_current and short_previous < long_previous:
                order_volume = self.context.risk_manager.calculate_position_volume(asset.ticker)
                return events.SignalEventMarketBuy(asset, order_volume)
            elif short_current < long_current and short_previous > long_previous:
                # TODO: Implement method to get remaining volume of first position to be exited
                order_volume = 5
                return events.SignalEventMarketSell(asset, order_volume)
            else:
                pass

        except TypeError:
            pass

