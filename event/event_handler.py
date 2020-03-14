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
                    print("Backtesting is still active")
                    pass
                else:
                    print("Backtesting is no longer active")
                    break

            # Detecting any new events.
            # Common for live and backtesting
            self.event_stack.add(self.data_provider.detect_market_events())

            # Looping over events in event stack and handling them accordingly
            while True:
                try:
                    print("Getting event")
                    event = self.event_stack.get()
                    print("Number of events left in the stack: {}".format(len(self.event_stack.events)))
                except EventStackEmptyError:
                    break
                else:
                    if event:
                        self.handle_event()

    def handle_event(self):
        pass
        






