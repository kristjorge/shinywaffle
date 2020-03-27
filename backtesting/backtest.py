from datetime import timedelta
from datetime import datetime
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import Broker
from financial_assets.financial_assets import FinancialAsset
from event.event_handler import EventHandler
from strategy.strategy import TradingStrategy
from data.data_provider import BacktestDataProvider


intervals = ("1min",
             "5min",
             "15min",
             "30min",
             "60min",
             "daily",
             "weekly",
             "monthly"
             "yearly")


class Backtester:

    """
    Class for holding the backtesting code

    """

    def __init__(self, portfolio, broker, trading_assets, time_increment, run_from=None, run_to=None):
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
        # Creating a list of datetime objects between backtest_from to backtest_to with the time_increment step size
        if self.time_increment == "daily":
            dt = 1
        elif self.time_increment == "60min":
            dt = 1 / 24
        elif self.time_increment == "30min":
            dt = 1 / (24*2)
        elif self.time_increment == "15min":
            dt = 1 / (24*2*2)
        elif self.time_increment == "5min":
            dt = 1 / (24*2*2*3)
        elif self.time_increment == "1min":
            dt = 1 / (24*2*2*3*5)
        else:
            dt = 1

        num_steps = int((self.backtest_to - self.backtest_from).days / dt)
        self.times = [self.backtest_from + i*timedelta(days=dt) for i in range(0, num_steps)]

    def copy(self):
        stocks = [s for s in self.assets.values()]
        return Backtester(self.portfolio, self.broker, stocks, self.time_increment)

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
            'initial portfolio holding': self.portfolio.holding,
            'base currency': self.portfolio.base_currency,
            'broker': self.broker.name,
            'assets': [asset.self2dict() for asset in self.assets.values()],
            # 'strategies': [strategy.self2dict() for strategy in self.strategies.values()]
            'strategies': {asset.strategies.keys() for asset in self.assets}
        }

        return data

    def run(self):
        EventHandler(portfolio=self.portfolio,
                     broker=self.broker,
                     assets=self.assets,
                     data_provider=self.data_provider)


class BacktestContainer:

    def __init__(self, name, parameters, backtester, path, run_no, sub_run_no, stochastic_run_no):
        self.name = name
        self.parameters = parameters
        self.backtester = backtester
        self.path = path
        self.run_no = run_no
        self.sub_run_no = sub_run_no
        self.stochastic_run_no = stochastic_run_no
        self.json_path = path + "_summary.json"

    def self2dict(self):
        # data = {}
        # attributes = [a for a in dir(self) if not a.startswith("__")
        #               and not callable(getattr(self, a))
        #               and not isinstance(getattr(self, a), Backtester)]
        #
        # for attr in attributes:
        #     data[attr] = getattr(self, attr)

        data = {
            "name": self.name,
            "parameters": self.parameters,
            "path": self.path,
            "run number": self.run_no,
            "sub run number": self.sub_run_no,
            "stochastic run number": self.stochastic_run_no,
            "summary file path": self.json_path
        }

        return data




            







