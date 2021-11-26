from shinywaffle.common.context import Context
from shinywaffle.common.event import events
from shinywaffle.common.assets import Asset
from shinywaffle.backtesting.orders import ANY_ORDER_TYPE
from abc import ABC, abstractmethod
from typing import List


class TradingStrategy(ABC):

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

    def generate_signal(self, asset: Asset) -> List[ANY_ORDER_TYPE]:
        """
        A function that calls the trading logic function that evaluates the latest time series data and generates
        trading signal based on the coded rules of the strategy. This method compares the asset.ticker with the
        tickers in the self.asset dict (the dictionary keys are the tickers). If the ticker of the passed asset
        object is contained in the list of keys, meaning that the strategy applies to the passed asset, then
        the trading logic is called and the signals are stored in a list of signals.

        An assertion is made that the events from the trading logic are indeed valid SignalEvents that would be
        possible for a trading strategy to pass.

        param asset: An asset object

        Returns: A list of events to be handles by the event handler
        """
        if asset.ticker in self.assets.keys():
            signals = [self.trading_logic(asset)]
            for signal in signals:
                if not isinstance(signal, events.SignalEventMarketBuy) or \
                        not isinstance(signal, events.SignalEventMarketSell) or \
                        not isinstance(signal, events.SignalEventLimitSell) or \
                        not isinstance(signal, events.SignalEventLimitBuy):
                    raise TypeError('Generated event needs to be of the type events.SignalEventMarketBuy, ' \
                                    'events.SignalEventMarketSell, events.SignalEventLimitBuy or ' \
                                    'events.SignalEventLimitSell')

            return signals
        else:
            pass  # Do not need to return [None] if the trading_logic method didn't return any events?
            # return [None]

    @abstractmethod
    def trading_logic(self, asset: Asset) -> ANY_ORDER_TYPE:
        """
        This method needs to be overridden to include the logic behind the signal generation. This method needs to
        return events to the generate_signal method which will then be appended to a list of events and passed to the
        event handler

        """
        pass

    def apply_to_asset(self, *assets):
        """ Sets the trading strategy to apply to a list of asset objects"""
        from shinywaffle.common.assets import Asset
        for asset in assets:
            if not isinstance(asset, Asset):
                raise TypeError('asset must be an instance of Asset base class')
            self.assets[asset.ticker] = asset

    def report(self):

        attributes = [a for a in dir(self) if not a.startswith("__")
                      and not a.startswith("_")
                      and a not in dir("__builtins__")
                      and not hasattr(getattr(self, a), "__call__")
                      and not a == 'context' and not a == 'assets']

        data = {a: getattr(self, a) for a in attributes}

        return data



