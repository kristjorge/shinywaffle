from common.event.event_stack import EventStack, PostEventStack
from common.event.event_stack import EventStackEmptyError
from common.event import events
import data.data_provider
import time
from ..context import Context
from typing import Type


class EventHandler:

    def __init__(self, context: Context, data_provider: Type[data.data_provider.DataProvider]):

        self.context = context
        self.account = context.account
        self.broker = context.broker
        self.assets = context.assets
        self.data_provider = data_provider
        self.event_stack = EventStack()
        self.post_event_stack = PostEventStack()

        while True:
            try:
                # Detecting any new events and getting the latest time series data
                new_events = self.data_provider.retrieve_time_series_data()
            except data.data_provider.BacktestCompleteException:
                break
            else:
                self.event_stack.add(new_events)

            # Looping over events in event stack and handling them accordingly
            while True:
                try:
                    event = self.event_stack.get()
                    self.handle_event(event)
                except EventStackEmptyError:
                    self.event_stack.events += self.post_event_stack.dump()
                    break

            self.account.update()
            if not self.event_stack and not self.post_event_stack:
                try:
                    print("Sleeping {} seconds".format(data_provider.sleep_time))
                    time.sleep(data_provider.sleep_time)
                except AttributeError:
                    pass

            try:
                self.context.progress_bar.update()
            except AttributeError:
                pass

    def handle_event(self, event):
        if type(event) == events.TimeSeriesEvent:
            self.handle_time_series_events()

        elif type(event) == events.SignalEventMarketBuy:
            new_event = self.account.place_buy_order(event)
            self.event_stack.add(new_event)

        elif type(event) == events.SignalEventLimitBuy:
            new_event = self.account.place_buy_order(event)
            self.event_stack.add(new_event)

        elif type(event) == events.SignalEventMarketSell:
            new_event = self.account.place_sell_order(event)
            # self.event_stack.add(new_event)
            self.post_event_stack.add(new_event)

        elif type(event) == events.SignalEventLimitSell:
            new_event = self.account.place_sell_order(event)
            # self.event_stack.add(new_event)
            self.post_event_stack.add(new_event)

        elif type(event) == events.StopLossEvent:
            pass

        elif type(event) == events.TrailingStopEvent:
            pass

        elif type(event) == events.MarketBuyOrderPlacedEvent:
            # new_event = self.broker.buy_order_fill_confirmation(event)
            self.broker.add_to_orderbook()
            self.event_stack.add(new_event)

        elif type(event) == events.MarketSellOrderPlacedEvent:
            # new_event = self.broker.sell_order_fill_confirmation(event)
            self.broker.add_to_orderbook()
            self.event_stack.add(new_event)

        elif type(event) == events.LimitBuyOrderPlacedEvent:
            # new_event = self.broker.buy_order_fill_confirmation(event)
            self.broker.add_to_orderbook()
            self.event_stack.add(new_event)

        elif type(event) == events.LimitSellOrderPlacedEvent:
            # new_event = self.broker.sell_order_fill_confirmation(event)
            self.broker.add_to_orderbook()
            self.event_stack.add(new_event)

        elif type(event) == events.OrderFilledEvent:
            self.account.complete_order(event)

    def handle_time_series_events(self):
        # Create list of strategy objects that are linked to the asset that have generated the events (same ticker)
        # Loop over the strategies with the generated events and call generate_signal method
        generated_events = []
        for strategy in self.context.strategies.values():
            new_events = strategy.generate_signal()
            generated_events += new_events

        self.event_stack.add(generated_events)

