import os
from tools.alpha_vantage import AlphaVantage
from financial_assets.financial_assets import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from strategy.sma_crossover import AverageCrossOver
from backtesting.risk_management import RiskManager


ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver("SMA crossover", short=20, long=50)


# Nokia stocks
nokia = Stock("Nokia", "NOK", "USD")
nokia_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "NOK", outputsize="full", return_as_link=True)
nokia.set_bars(nokia_bars)
nokia.add_strategy(sma_strategy)
portfolio = Portfolio(1000, "USD", [nokia])
risk_manager = RiskManager(portfolio)
portfolio.set_risk_manager(risk_manager)

new_bars = nokia_bars.fetch()
a=1
