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
            # Specific for backtesting only
            if isinstance(self.data_provider, BacktestDataProvider):
                if self.data_provider.backtest_is_active:
                    day_of_the_week = utils.misc.get_weekday(data_provider.current_time.weekday())
                    print("Currently at time is {} {}".format(day_of_the_week, data_provider.current_time))
                else:
                    break

            # Detecting any new events and getting the latest time series data
            new_events = self.data_provider.detect_time_series_event()
            self.time_series_data = self.data_provider.get_time_series_data()
            self.event_stack.add(new_events)

            # Looping over events in event stack and handling them accordingly
            while True:
                try:
                    event = self.event_stack.get()
                    self.handle_event(event)
                except EventStackEmptyError:
                    break

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

