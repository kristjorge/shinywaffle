from datetime import datetime
from data.bar_provider import BarProvider
from backtesting.backtest import Backtester
from risk.risk_management import BaseRiskManager
from common.assets.assets import Stock
from common.account import Account
from backtesting.broker import BacktestBroker
from strategy.sma_crossover import AverageCrossOver
from strategy.random_signal_strategy import FixedDatesTransactionsStrategy
from common.context import Context

context = Context()

broker = BacktestBroker(context, 0, 0, 'USD')
trading_strategy = FixedDatesTransactionsStrategy(context)

# Nvidia stocks
nvidia = Stock(context, "Nvidia", "NVDA", "USD")
nvidia_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/NVDA_1D.csv', '%Y-%m-%d')
nvidia.set_bars(nvidia_bars)

# Oracle stocks
oracle = Stock(context, "Oracle", "ORCL", "USD")
oracle_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/ORCL_1D.csv', '%Y-%m-%d')
oracle.set_bars(oracle_bars)

# IBM stocks
ibm = Stock(context, "IBM", "IBM", "USD")
ibm_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/IBM_1D.csv', '%Y-%m-%d')
ibm.set_bars(ibm_bars)

trading_strategy.apply_to_asset(oracle, ibm)

risk_manager = BaseRiskManager(context)
account = Account(context, 1000, "USD", 2)
backtester = Backtester(context, 'daily', run_from=datetime(2011, 1, 1), run_to=datetime(2020, 1, 1))
backtester.run()
