import os
from data.bar_provider import BarProvider
from backtesting.backtest import Backtester
from financial_assets.financial_assets import Stock
from backtesting.account import Account
from backtesting.brokers import Broker
from strategy.sma_crossover import AverageCrossOver
from datetime import datetime


broker = Broker('My free broker', 0, 0, 'USD')
sma_strategy = AverageCrossOver("SMA crossover", short=20, long=50)


# Nvidia stocks
nvidia = Stock("Nvidia", "NVDA", "USD")
nvidia_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/NVDA_1D.csv', '1d', '%Y-%m-%d')
nvidia.set_bars(nvidia_bars)
nvidia.add_strategy(sma_strategy)

# Oracle stocks
oracle = Stock("Oracle", "ORCL", "USD")
oracle_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/ORCL_1D.csv', '1d', '%Y-%m-%d')
oracle.set_bars(oracle_bars)
oracle.add_strategy(sma_strategy)

# IBM stocks
ibm = Stock("IBM", "IBM", "USD")
ibm_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/IBM_1D.csv', '1d', '%Y-%m-%d')
ibm.set_bars(ibm_bars)
ibm.add_strategy(sma_strategy)

account = Account(1000, "USD", [nvidia, oracle, ibm], 2)
backtester = Backtester(account, broker, [nvidia, oracle, ibm], "daily", run_from=datetime(2010, 1, 1), run_to=datetime(2020, 1, 1))
backtester.run()
