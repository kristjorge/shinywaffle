from datetime import datetime
from data.bar_provider import BarProvider
from backtesting.backtest import Backtester
from common.risk_management import BaseRiskManager
from common.financial_assets.financial_assets import Stock
from common.account import Account
from backtesting.brokers import Broker
from strategy.random_signal_strategy import RandomSignalStrategy
from common.context import Context

context = Context()

broker = Broker(context, 'My free broker', 0, 0, 'USD')
random_signal_strat = RandomSignalStrategy()

# Nvidia stocks
nvidia = Stock(context, "Nvidia", "NVDA", "USD")
nvidia_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/NVDA_1D.csv', '1d', '%Y-%m-%d')
nvidia.set_bars(nvidia_bars)
nvidia.add_strategy(random_signal_strat)

# Oracle stocks
oracle = Stock(context, "Oracle", "ORCL", "USD")
oracle_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/ORCL_1D.csv', '1d', '%Y-%m-%d')
oracle.set_bars(oracle_bars)
oracle.add_strategy(random_signal_strat)

# IBM stocks
ibm = Stock(context, "IBM", "IBM", "USD")
ibm_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/IBM_1D.csv', '1d', '%Y-%m-%d')
ibm.set_bars(ibm_bars)
ibm.add_strategy(random_signal_strat)

risk_manager = BaseRiskManager(context)
account = Account(context, 1000, "USD", 2)
backtester = Backtester(context, 'daily', run_from=datetime(2010, 1, 1), run_to=datetime(2020, 1, 1))
second_context = context.copy()
backtester.run()
