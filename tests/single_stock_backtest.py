import os
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from financial_assets.financial_assets import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from strategy.sma_crossover import AverageCrossOver
from datetime import datetime


ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver("SMA crossover", short=20, long=50)


# Equinor stocks
equinor = Stock("Equinor Energy", "EQNR", "USD")
equinor_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "EQNR", outputsize="full")
exxon_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "XON", outputsize="full")

equinor.set_bars(equinor_bars)
equinor.add_data_series("exxon_bars", exxon_bars)
equinor.add_strategy(sma_strategy)


portfolio = Portfolio(500, "USD", [equinor])

test_sample = equinor_bars.sample_datetime(datetime(2019, 6, 1))

backtester = Backtester(portfolio, ib, [equinor], "daily", run_to=datetime(2020, 1, 1))
backtester.run()
