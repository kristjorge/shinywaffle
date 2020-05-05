import os
from datetime import timedelta
from datetime import datetime
from common.event.event_handler import EventHandler
from data.data_provider import BacktestDataProvider
from backtesting.reporter import Reporter
from utils.misc import get_backtest_dt, get_datetime_format
from common.context import Context
from utils.progress_bar import ProgressBar


class Backtester:

    """
    Class for holding the backtesting code

    """

    def __init__(self, context: Context, time_increment: str, run_from: datetime = None,
                 run_to: datetime = None, path: str = os.getcwd(),
                 filename: str = "Summary {}".format(datetime.now().strftime("%d-%m-%Y %H%M%S"))):

        self.context = context
        self.account = context.account
        self.broker = context.broker
        self.assets = context.assets
        self.time_increment = get_datetime_format(time_increment)
        self.datetime_format = self.time_increment
        self.reporter = Reporter(path=path, filename=filename)
        self.event_handler = None

        self.run_from = run_from
        self.run_to = run_to

        if self.run_from is not None:
            assert isinstance(self.run_from, datetime)
        if self.run_to is not None:
            assert isinstance(self.run_to, datetime)

        self.times = list()
        self.make_times()
        self.data_provider = BacktestDataProvider(self.context, self.times)

    def make_times(self):

        dt = get_backtest_dt(self.time_increment)
        num_steps = int((self.backtest_to - self.backtest_from).days / dt)
        self.times = [self.backtest_from + i*timedelta(days=dt) for i in range(0, num_steps)]

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

    def self2dict(self):
        data = {
            'initial account holding': self.account.initial_holding,
            'broker': self.broker.self2dict(),
            'assets': [asset.self2dict() for asset in self.assets.values()],
            'backtest from': self.backtest_from.strftime(self.datetime_format),
            'backtest to': self.backtest_to.strftime(self.datetime_format),
            'account': self.account.self2dict(),
            'events': self.event_handler.event_stack.self2dict()
        }
        return data

    def run(self):
        self.context.progress_bar = ProgressBar(len(self.times))
        self.event_handler = EventHandler(self.context, data_provider=self.data_provider)
        self.reporter.aggregate_report(self.self2dict())


class BacktestContainer:

    def __init__(self,
                 name: str, parameters: dict, backtester: Backtester, path: str,
                 run_no: int, sub_run_no: int, stochastic_run_no: int):

        self.name = name
        self.parameters = parameters
        self.backtester = backtester
        self.path = path
        self.run_no = run_no
        self.sub_run_no = sub_run_no
        self.stochastic_run_no = stochastic_run_no
        self.json_path = self.backtester.reporter.path + "/" + self.backtester.reporter.filename + ".json"

    def self2dict(self):
        data = {
            'name': self.name,
            'parameters': self.parameters,
            'path': self.path,
            'run number': self.run_no,
            'sub run number': self.sub_run_no,
            'stochastic run number': self.stochastic_run_no,
            'summary file path': self.json_path,
        }

        return data
