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
                self.portfolio.update(self.time_series_data)

    def handle_event(self, event):
        if type(event) == events.TimeSeriesEvent:
            self.handle_time_series_events(event)

        elif type(event) == events.SignalEventBuy:
            pass

        elif type(event) == events.SignalEventSell:
            pass

        elif type(event) == events.StopLossEvent:
            pass

        elif type(event) == events.TrailingStopEvent:
            pass

        elif type(event) == events.MarketOrderEvent:
            pass

        elif type(event) == events.LimitOrderEvent:
            pass

        elif type(event) == events.OrderFillEvent:
            pass

    def handle_time_series_events(self, event):
        # Create list of strategy objects that are linked to the asset that have generated the events (same ticker)
        # Loop over the strategies with the generated events and call generate_signal method
        generated_events = []
        for strategy in [s for s in self.assets[event.asset.ticker].strategies.values()]:
            time_series_data = self.time_series_data[event.asset.ticker]
            time_series_data["asset"] = event.asset.ticker
            new_event = strategy.generate_signal(time_series_data)
            if new_event is not None:
                generated_events.append(new_event)

        self.event_stack.add(generated_events)

