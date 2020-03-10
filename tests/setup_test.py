import os
from backtesting.backtest import Backtester
from backtesting.stock.stock import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from tools.alpha_vantage import AlphaVantage
from strategy.sma_crossover import AverageCrossOver

acc = Portfolio(500, "USD")
ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])

# Equinor stocks
equinor = Stock("Equinor Energy", "EQNR")
equinor.add_strategy(AverageCrossOver("SMA crossover", short=10, long=25))
equinor_bars = alpha_vantage.query("TIME_SERIES_DAILY_ADJUSTED", "EQNR", output_as_bars=True, reverse=True)
equinor.set_bars(equinor_bars, "daily")

backtester = Backtester(acc, ib, [equinor], "daily")




