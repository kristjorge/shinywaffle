import os
from datetime import timedelta
from datetime import datetime
from shinywaffle.common.event.event_handler import EventHandler
from shinywaffle.data.data_provider import BacktestDataProvider
from shinywaffle.backtesting.reporter import Reporter
from shinywaffle.utils import misc
from shinywaffle.common.context import Context
from shinywaffle.utils.progress_bar import ProgressBar
from typing import List


class Backtester:

    """
    Class for holding the backtesting code
    """

    def __init__(self, context: Context, time_increment: str, run_from: datetime = None,
                 run_to: datetime = None, path: str = os.getcwd(),
                 filename: str = "Backtest {}".format(datetime.now().strftime("%d-%m-%Y %H%M%S"))):

        self.context = context
        self.account = context.account
        self.broker = context.broker
        self.assets = context.assets
        self.time_increment = time_increment
        self.datetime_format = misc.get_datetime_format(time_increment)
        self.reporter = Reporter(path=path, filename=filename)
        self.event_handler = None

        self.run_from = run_from
        self.run_to = run_to

        if self.run_from is not None:
            assert isinstance(self.run_from, datetime)
        if self.run_to is not None:
            assert isinstance(self.run_to, datetime)

        self.times = self.make_times()
        self.data_provider = BacktestDataProvider(self.context, self.times)

    def make_times(self) -> List[datetime]:
        dt = misc.get_backtest_dt(self.time_increment)
        num_steps = int((self.backtest_to - self.backtest_from).days / dt)
        return [self.backtest_from + i*timedelta(days=dt) for i in range(0, num_steps)]

    def copy(self):
        return Backtester(self.context.copy(), self.time_increment, self.run_from, self.run_to)

    @property
    def backtest_from(self):
        if self.run_from is not None:
            return self.run_from
        else:
            return min([s.bars[-1].datetime for ticker, s in self.assets.items()])

    @property
    def backtest_to(self):
        if self.run_to is not None:
            return self.run_to
        else:
            return max([s.bars[0].datetime for ticker, s in self.assets.items()])

    def report(self):
        data = {
            'initial holding': self.account.initial_holding,
            'broker': self.broker.report(),
            'assets': [asset.report() for asset in self.assets.values()],
            'strategies': [s.report() for s in self.context.strategies.values()],
            'backtest from': self.backtest_from.strftime(self.datetime_format),
            'backtest to': self.backtest_to.strftime(self.datetime_format),
            'account': self.account.report(),
            'times': [t.strftime(self.datetime_format) for t in self.context.times],
            'events': self.event_handler.event_stack.report()
        }
        return data

    def run(self):
        self.context.progress_bar = ProgressBar(len(self.times))
        self.event_handler = EventHandler(self.context, data_provider=self.data_provider)
        self.reporter.aggregate_report(self.report())
