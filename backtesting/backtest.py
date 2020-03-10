from datetime import datetime
from datetime import timedelta
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import Broker
from backtesting.stock.stock import Stock
from event.event_loop import EventLoop

"""
Class for holding the backtesting code

"""

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

    def __init__(self, portfolio, broker, active_stocks, time_increment):
        """

        :param portfolio: Object describing the trading account (type Account)
        :param broker: Broker object holding order logic and pricing (type Broker)
        :param active_stocks: List of stocks used in the backtesting (type list)
        """

        assert isinstance(portfolio, Portfolio)
        assert isinstance(broker, Broker)
        assert isinstance(active_stocks, list)

        self.portfolio = portfolio
        self.broker = broker
        self.stocks = dict()
        self.strategies = dict()
        self.time_increment = time_increment

        # Looping through the list of provided stocks and append them to the self.stocks dictionary with the
        # ticker as they key and the Stock object as the value
        for stock in active_stocks:
            assert isinstance(stock, Stock), "All stocks in the list of stocks must of the \
                                                                    correct class instance"
            assert stock.strategies, "{} must have a specified trading strategy".format(stock.name)
            assert hasattr(stock.series, "bars"), "{} must have historical price data attached to it".format(stock.name)

            if stock.ticker in self.stocks:
                print("Replacing previously specified stock with same ticker")

            self.stocks[stock.ticker] = stock
        self.times = list()
        self.make_times()

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
        stocks = [s for s in self.stocks.values()]
        return Backtester(self.portfolio, self.broker, stocks, self.time_increment)

    @property
    def backtest_from(self):
        return min([s.series.bars[0].datetime for ticker, s in self.stocks.items()])

    @property
    def backtest_to(self):
        return max([s.series.bars[-1].datetime for ticker, s in self.stocks.items()])

    def self2dict(self):
        data = {
            'initial portfolio holding': self.portfolio.holding,
            'base currency': self.portfolio.base_currency,
            'broker': self.broker.name,
            'stocks': [stock.self2dict() for ticker, stock in self.stocks.items()],
        }

        return data

    def run(self):
        EventLoop(self.stocks, self.portfolio, self.broker)


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
        data = {}
        attributes = [a for a in dir(self) if not a.startswith("__")
                      and not callable(getattr(self, a))
                      and not isinstance(getattr(self, a), Backtester)]

        for attr in attributes:
            data[attr] = getattr(self, attr)

        return data




            







