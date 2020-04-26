import os
from datetime import timedelta
from datetime import datetime
from backtesting.account import Account
from backtesting.brokers import Broker
from financial_assets.financial_assets import FinancialAsset
from event.event_handler import EventHandler
from data.data_provider import BacktestDataProvider
from backtesting.reporter import Reporter
from utils.misc import get_backtest_dt, get_datetime_format


class Backtester:

    """
    Class for holding the backtesting code

    """

    def __init__(self,
                 account: Account, broker: Broker, trading_assets: list, time_increment: str, run_from: datetime = None,
                 run_to: datetime = None, path: str = os.getcwd(),
                 filename: str = "Summary {}".format(datetime.now().strftime("%d-%m-%Y %H%M%S"))):
        """

        :param account: Object describing the trading account (type Account)
        :param broker: Broker object holding order logic and pricing (type Broker)
        :param trading_assets: List of stocks used in the backtesting (type list)
        """

        assert isinstance(account, Account)
        assert isinstance(broker, Broker)
        assert isinstance(trading_assets, list)

        self.account = account
        self.broker = broker
        self.assets = dict()
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

        # Looping through the list of provided assets and strategies and append them to the self.stocks and
        for asset in trading_assets:
            assert isinstance(asset, FinancialAsset)
            assert hasattr(asset, "bars"), "{} must have historical price data attached to it".format(asset.name)
            self.assets[asset.ticker] = asset

        self.make_times()
        self.data_provider = BacktestDataProvider(self.assets, self.times)

    def make_times(self):

        dt = get_backtest_dt(self.time_increment)
        num_steps = int((self.backtest_to - self.backtest_from).days / dt)
        self.times = [self.backtest_from + i*timedelta(days=dt) for i in range(0, num_steps)]

    def copy(self):
        assets = [s for s in self.assets.values()]
        return Backtester(self.account, self.broker, assets, self.time_increment, self.run_from, self.run_to)

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
            'base currency': self.account.base_currency,
            'broker': self.broker.self2dict(),
            'assets': [asset.self2dict() for asset in self.assets.values()],
            'strategies': {asset.name: [s.self2dict() for s in asset.strategies.values()] for asset in self.assets.values()},
            'backtest from': self.backtest_from.strftime("%d-%m-%Y %H:%M:%S"),
            'backtest to': self.backtest_to.strftime("%d-%m-%Y %H:%M:%S"),
            'account': self.account.self2dict(),
            'events': self.event_handler.event_stack.self2dict()
        }
        return data

    def run(self):
        self.event_handler = EventHandler(account=self.account,
                                          broker=self.broker,
                                          assets=self.assets,
                                          data_provider=self.data_provider)
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




            







