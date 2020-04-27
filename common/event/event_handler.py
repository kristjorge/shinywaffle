from common.event.event_stack import EventStack
from common.event.event_stack import EventStackEmptyError
from common.event import events
import data.data_provider
import time
from backtesting.account import Account
from backtesting.brokers import Broker
from typing import Type


class EventHandler:

    def __init__(self, account: Account, broker: Type[Broker], assets: dict,
                 data_provider: Type[data.data_provider.DataProvider]):
        self.account = account
        self.broker = broker
        self.assets = assets
        self.data_provider = data_provider
        self.event_stack = EventStack()
        self.time_series_data = {}

        while True:
            try:
                # Detecting any new events and getting the latest time series data
                new_events, self.time_series_data = self.data_provider.get_time_series_data()
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
                    break

            self.account.update_portfolio(self.time_series_data)
            if type(data_provider) == data.data_provider.LiveDataProvider:
                print("Sleeping {} seconds".format(data_provider.sleep_time))
                time.sleep(data_provider.sleep_time)

    def handle_event(self, event):
        if type(event) == events.TimeSeriesEvent:
            self.handle_time_series_events(event)

        elif type(event) == events.SignalEventBuy:
            # New event is 1) MarketOrderEvent or 2) LimitOrderEvent
            order_size = self.account.risk_manager.calculate_position_size()
            new_event = self.account.place_buy_order(event.asset, order_size)
            self.event_stack.add(new_event)

        elif type(event) == events.SignalEventSell:
            # New event is 1) MarketOrderEvent or 2) LimitOrderEvent
            order_size = self.account.risk_manager.calculate_position_size()
            new_event = self.account.place_sell_order(event.asset, order_size)
            self.event_stack.add(new_event)

        elif type(event) == events.StopLossEvent:
            pass

        elif type(event) == events.TrailingStopEvent:
            pass

        elif type(event) == events.MarketOrderBuyEvent:
            # New event is of type OrderFilledEvent
            price = self.broker.request_buy_order_price(self.time_series_data[event.asset.ticker])
            new_event = self.broker.fill_buy_order(event, price)
            self.event_stack.add(new_event)

        elif type(event) == events.MarketOrderSellEvent:
            # New event is of type OrderFilledEvent
            price = self.broker.request_sell_order_price(self.time_series_data[event.asset.ticker])
            new_event = self.broker.fill_sell_order(event, price, max_volume=event.max_volume)
            self.event_stack.add(new_event)

        elif type(event) == events.LimitOrderBuyEvent:
            pass

        elif type(event) == events.LimitOrderSellEvent:
            pass

        elif type(event) == events.OrderFilledEvent:
            self.account.register_order(event, self.time_series_data['current time'])

    def handle_time_series_events(self, event):
        # Create list of strategy objects that are linked to the asset that have generated the events (same ticker)
        # Loop over the strategies with the generated events and call generate_signal method
        generated_events = []
        for strategy in [s for s in self.assets[event.asset.ticker].strategies.values()]:
            time_series_data = self.time_series_data[event.asset.ticker]
            time_series_data['asset'] = event.asset
            new_event = strategy.generate_signal(time_series_data)
            generated_events.append(new_event)

        self.event_stack.add(generated_events)

