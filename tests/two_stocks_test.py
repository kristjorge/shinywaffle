import os
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from common.financial_assets.assets import Stock
from common.account import Account
from backtesting.brokers import Broker
from strategy.sma_crossover import AverageCrossOver
from datetime import datetime
from risk.risk_management import BaseRiskManager
from common.context import Context

context = Context()

broker = Broker('My free broker', 0, 0, 'USD')
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver(short=20, long=50)


# Nokia stocks
nokia = Stock("Nokia", "NOK", "USD")
nokia_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "NOK", outputsize="full")
nokia.set_bars(nokia_bars)
nokia.add_strategy(sma_strategy)

# Ford stocks
# ford = Stock("Ford", "F", "USD")
# ford_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "F", outputsize="full")
# ford.set_bars(ford_bars)
# ford.add_strategy(sma_strategy)

risk_manager = BaseRiskManager()
portfolio = Account(1000, "USD", num_base_decimals=2)
backtester = Backtester(context, 'daily', run_from=datetime(2005, 1, 1), run_to=datetime(2020, 1, 1))
backtester.run()
