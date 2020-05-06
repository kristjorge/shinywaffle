from common.context import Context
from common.event import events


class TradingStrategy:

    """

Base class for trading strategies used in either backtesting or live trading.
All implemented strategies must inherit from this super class

Functions:
    - link: Link the strategy object to a financial asset object
    - generate_signal: Evaluates data and generates a signal either "buy" or "sell"
    - self2dict: Generating the main meta data for the objects in a dict that can be dumped into a json file

"""

    def __init__(self, context: Context, name):
        self.name = name
        self.assets = {}
        self.context = context
        self.context.strategies[self.name] = self

    def generate_signal(self, asset) -> list:
        if asset.ticker in self.assets.keys():
            signals = [self.trading_logic(asset)]
            if signals:
                assert all([type(s) == events.SignalEventMarketBuy or
                            type(s) == events.SignalEventMarketSell or
                            type(s) == events.SignalEventLimitBuy or
                            type(s) == events.SignalEventLimitSell or
                            s is None for
                            s in signals]), 'Generated event needs to be of the type events.SignalEventMarketBuy, ' \
                                            'events.SignalEventMarketSell, events.SignalEventLimitBuy or ' \
                                            'events.SignalEventLimitSell'
            return signals
        else:
            return [None]

    def trading_logic(self, asset):
        """
        This method needs to be overridden to include the logic behind the signal generation. This method needs to
        return events to the generate_signal method which will then be appended to a list of events and passed to the
        event handler

        """
        raise NotImplementedError

    def apply_to_asset(self, *assets):
        from common.assets.assets import Asset
        for asset in assets:
            assert isinstance(asset, Asset)
            self.assets[asset.ticker] = asset

    def report(self):

        attributes = [a for a in dir(self) if not a.startswith("__")
                      and not a.startswith("_")
                      and a not in dir("__builtins__")
                      and not hasattr(getattr(self, a), "__call__")
                      and not a == 'context' and not a == 'assets']

        data = {a: getattr(self, a) for a in attributes}

        return data



