from datetime import datetime
from data.bar_provider import BarProvider
from backtesting.backtest import Backtester
from backtesting.risk_management import BaseRiskManager
from financial_assets.financial_assets import Stock
from backtesting.account import Account
from backtesting.brokers import Broker
from strategy.random_signal_strategy import RandomSignalStrategy


broker = Broker('My free broker', 0, 0, 'USD')
random_signal_strat = RandomSignalStrategy("Random test strategy")


# Nvidia stocks
nvidia = Stock("Nvidia", "NVDA", "USD")
nvidia_bars = BarProvider('/shiny-waffle/data/yahoo_finance/NVDA_1D.csv', '1d', '%Y-%m-%d')
nvidia.set_bars(nvidia_bars)
nvidia.add_strategy(random_signal_strat)

# Oracle stocks
oracle = Stock("Oracle", "ORCL", "USD")
oracle_bars = BarProvider('/shiny-waffle/data/yahoo_finance/ORCL_1D.csv', '1d', '%Y-%m-%d')
oracle.set_bars(oracle_bars)
oracle.add_strategy(random_signal_strat)

# IBM stocks
ibm = Stock("IBM", "IBM", "USD")
ibm_bars = BarProvider('/shiny-waffle/data/yahoo_finance/IBM_1D.csv', '1d', '%Y-%m-%d')
ibm.set_bars(ibm_bars)
ibm.add_strategy(random_signal_strat)

account = Account(1000, "USD", [nvidia, oracle, ibm], 2)
account.set_risk_manager(BaseRiskManager(account))
backtester = Backtester(account, broker, [nvidia, oracle, ibm], "daily",
                        run_from=datetime(2010, 1, 1), run_to=datetime(2020, 1, 1))
backtester.run()
