import os
from datetime import timedelta
from datetime import datetime
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import Broker
from financial_assets.financial_assets import FinancialAsset
from event.event_handler import EventHandler
from data.data_provider import BacktestDataProvider
from backtesting.reporter import Reporter
from utils.misc import get_backtest_dt


class Backtester:

    """
    Class for holding the backtesting code

    """

    def __init__(self, portfolio, broker, trading_assets, time_increment, run_from=None, run_to=None, path=os.getcwd(),
                 filename="Summary {}".format(datetime.now().strftime("%d-%m-%Y %H%M%S"))):
        """

        :param portfolio: Object describing the trading account (type Account)
        :param broker: Broker object holding order logic and pricing (type Broker)
        :param trading_assets: List of stocks used in the backtesting (type list)
        """

        assert isinstance(portfolio, Portfolio)
        assert isinstance(broker, Broker)
        assert isinstance(trading_assets, list)

        self.portfolio = portfolio
        self.broker = broker
        self.assets = dict()
        self.time_increment = time_increment
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

        get_backtest_dt(self.time_increment)
        num_steps = int((self.backtest_to - self.backtest_from).days / dt)
        self.times = [self.backtest_from + i*timedelta(days=dt) for i in range(0, num_steps)]

    def copy(self):
        assets = [s for s in self.assets.values()]
        return Backtester(self.portfolio, self.broker, assets, self.time_increment, self.run_from, self.run_to)

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
            'initial portfolio holding': self.portfolio.initial_holding,
            'base currency': self.portfolio.base_currency,
            'broker': self.broker.self2dict(),
            'assets': [asset.self2dict() for asset in self.assets.values()],
            'strategies': {asset.name: [s.self2dict() for s in asset.strategies.values()] for asset in self.assets.values()},
            'backtest from': self.backtest_from.strftime("%d-%m-%Y %H:%M:%S"),
            'backtest to': self.backtest_to.strftime("%d-%m-%Y %H:%M:%S"),
            'portfolio': self.portfolio.self2dict(),
            'events': self.event_handler.event_stack.self2dict()
        }
        return data

    def run(self):
        self.event_handler = EventHandler(portfolio=self.portfolio,
                             broker=self.broker,
                             assets=self.assets,
                             data_provider=self.data_provider)
        self.reporter.aggregate_report(self.self2dict())


class BacktestContainer:

    def __init__(self, name, parameters, backtester, path, run_no, sub_run_no, stochastic_run_no):
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




            







