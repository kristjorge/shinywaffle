from event.event_stack import EventStack
from event.event_stack import EventStackEmptyError
from data.data_provider import BacktestingDataProvider
from data.data_provider import LiveDataProvider
from data.data_provider import DataProvider
from utils.misc import get_weekday


class EventHandler:

    def __init__(self, portfolio, broker, strategies, data_provider):
        self.portfolio = portfolio
        self.broker = broker
        self.strategies = strategies
        self.data_provider = data_provider
        self.event_stack = EventStack()
        self.time_series_data = dict()

        assert isinstance(self.data_provider, DataProvider)

        while True:
            # Specific for backtesting only
            if isinstance(self.data_provider, BacktestingDataProvider):
                if self.data_provider.backtest_is_active:
                    day_of_the_week = get_weekday(data_provider.latest_past_time.weekday())
                    print("Currently at time: {} {}".format(day_of_the_week, data_provider.latest_past_time))
                else:
                    break

            # Detecting any new events.
            # Common for live and backtesting
            self.data_provider.detect_time_series_event(self.event_stack)

            # Looping over events in event stack and handling them accordingly
            while True:
                try:
                    event = self.event_stack.get()
                    self.handle_event(event)
                except EventStackEmptyError:
                    break

    def handle_event(self, event):
        if event.event_type == "TIME_SERIES":
            print("Time series signal detected")

            # Create list of strategy objects that are linked to the asset that have generated the events (same ticker)
            # Loop over the strategies with the generated events and call generate_signal method
            generated_events = []
            strategies = [s for s in self.strategies.values() if event.asset.ticker in s.assets]
            for strategy in strategies:
                new_event = strategy.generate_signal(event.asset)
                if new_event is not None:
                    generated_events.append(new_event)

            self.event_stack.add(generated_events)

        elif event.event_type == "SIGNAL BUY":
            print("Buy signal detected")

        elif event.event_type == "SIGNAL SELL":
            pass

        elif event.event_type == "STOP":
            pass

        elif event.event_type == "ORDER":
            pass

        elif event.event_type == "FILL":
            pass



        






