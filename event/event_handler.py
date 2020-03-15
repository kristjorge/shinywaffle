from event.event_stack import EventStack
from event.event_stack import EventStackEmptyError
from event.data_provider import BacktestingDataProvider


class EventHandler:

    def __init__(self, portfolio, broker, strategies, data_provider):
        self.portfolio = portfolio
        self.broker = broker
        self.strategies = strategies
        self.data_provider = data_provider
        self.event_stack = EventStack()
        self.time_series_data = dict()

        while True:
            # Specific for backtesting only
            if isinstance(self.data_provider, BacktestingDataProvider):
                if self.data_provider.backtest_is_active:
                    pass
                else:
                    break

            # Detecting any new events.
            # Common for live and backtesting
            self.event_stack.add(self.data_provider.detect_time_series_event())

            # Looping over events in event stack and handling them accordingly
            while True:
                try:
                    event = self.event_stack.get()
                    self.handle_event(event)
                except EventStackEmptyError:
                    break

    def handle_event(self, event):

        if event.event_type == "TIME_SERIES":
            pass
        elif event.event_type == "SIGNAL":
            pass
        elif event.event_type == "STOP":
            pass
        elif event.event_type == "ORDER":
            pass
        elif event.event_type == "FILL":
            pass



        






