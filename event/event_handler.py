from event.event_stack import EventStack
from event.event_stack import EventStackEmptyError
from data.data_provider import BacktestDataProvider
from event import events
import utils.misc
import data.data_provider


class EventHandler:

    def __init__(self, portfolio, broker, assets, data_provider):
        self.portfolio = portfolio
        self.broker = broker
        self.assets = assets
        self.data_provider = data_provider
        self.event_stack = EventStack()
        self.time_series_data = {}

        assert isinstance(self.data_provider, data.data_provider.DataProvider)

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

            # Update data - only relevant for backtesting
            if type(data_provider) == BacktestDataProvider:

                # Updating portfolio value
                self.portfolio.update_portfolio(self.time_series_data)

    def handle_event(self, event):
        if type(event) == events.TimeSeriesEvent:
            self.handle_time_series_events(event)

        elif type(event) == events.SignalEventBuy:
            # TODO: Implement logic to decide between market and limit orders
            # New event is 1) MarketOrderEvent or 2) LimitOrderEvent
            order_size = self.portfolio.risk_manager.calculate_position_size()
            # new_event = self.portfolio.place_order(event.asset, order_size, "buy")
            new_event = self.portfolio.place_buy_order(event.asset, order_size)
            self.event_stack.add(new_event)

        elif type(event) == events.SignalEventSell:
            # New event is 1) MarketOrderEvent or 2) LimitOrderEvent
            # TODO: Implement logic to limit number of asset sold to the number available in the portfolio
            order_size = self.portfolio.risk_manager.calculate_position_size()
            # new_event = self.portfolio.place_order(event.asset, order_size, "sell")
            new_event = self.portfolio.place_sell_order(event.asset, order_size)
            self.event_stack.add(new_event)

        elif type(event) == events.StopLossEvent:
            pass

        elif type(event) == events.TrailingStopEvent:
            pass

        elif type(event) == events.MarketOrderBuyEvent:
            # New event is of type OrderFilledEvent
            price = self.broker.request_order_price(self.time_series_data[event.asset.ticker])
            new_event = self.broker.fill_buy_order(event, price)
            self.event_stack.add(new_event)

        elif type(event) == events.MarketOrderSellEvent:
            # New event is of type OrderFilledEvent
            price = self.broker.request_order_price(self.time_series_data[event.asset.ticker])
            new_event = self.broker.fill_sell_order(event, price, max_volume=event.max_volume)
            self.event_stack.add(new_event)

        elif type(event) == events.LimitOrderBuyEvent:
            pass

        elif type(event) == events.LimitOrderSellEvent:
            pass

        elif type(event) == events.OrderFilledEvent:
            self.portfolio.register_order(event)

    def handle_time_series_events(self, event):
        # Create list of strategy objects that are linked to the asset that have generated the events (same ticker)
        # Loop over the strategies with the generated events and call generate_signal method
        generated_events = []
        for strategy in [s for s in self.assets[event.asset.ticker].strategies.values()]:
            time_series_data = self.time_series_data[event.asset.ticker]
            time_series_data["asset"] = event.asset
            new_event = strategy.generate_signal(time_series_data)
            generated_events.append(new_event)

        self.event_stack.add(generated_events)

