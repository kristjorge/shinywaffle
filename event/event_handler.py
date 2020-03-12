from event.event_stack import EventStack


class EventHandler:

    def __init__(self, portfolio, broker, strategies, data_provider, mode):
        self.portfolio = portfolio
        self.broker = broker
        self.strategies = strategies
        self.data_provider = data_provider
        self.stack = EventStack()

        assert mode == "backtest" or mode == "live"

        if mode == "backtest":
            self.run_backtest()
        elif mode == "live":
            self.run_live()

    def run_backtest(self):
        while True:
            if self.data_provider.backtest_is_active:
                self.data_provider.provide_time_series_data() # Return the new datetime object and all time series data objects
            else:
                break

    def run_live(self):
        pass




