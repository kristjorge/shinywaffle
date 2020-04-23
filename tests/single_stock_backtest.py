import os
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from financial_assets.financial_assets import Stock
from backtesting.account import Account
from backtesting.broker.brokers import InteractiveBrokers
from strategy.sma_crossover import AverageCrossOver
from datetime import datetime
from backtesting.risk_management import RiskManager


ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver("SMA crossover", short=20, long=50)


# Nokia stocks
nokia = Stock("Nokia", "NOK", "USD")
nokia_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "NOK", outputsize="full")
nokia.set_bars(nokia_bars)
nokia.add_strategy(sma_strategy)
account = Account(1000, "USD", [nokia])
risk_manager = RiskManager(account)
account.set_risk_manager(risk_manager)
backtester = Backtester(account, ib, [nokia], time_increment="weekly", run_to=datetime(2005, 1, 1))
backtester.run()
