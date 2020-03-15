import os
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from financial_assets.stock import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from strategy.sma_crossover import AverageCrossOver
from backtesting.workflow.uncertainty_variable import UncertaintyVariable
from utils.time_series_data import TimeSeriesDataReader

portfolio = Portfolio(500, "USD")
ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver("SMA crossover", short=UncertaintyVariable("short"), long=UncertaintyVariable("long"))


# Equinor stocks
equinor = Stock("Equinor Energy", "EQNR")
equinor_bars = alpha_vantage.query("TIME_SERIES_DAILY_ADJUSTED", "EQNR", output_as_bars=True, reverse=True)
financial_reports = TimeSeriesDataReader().read_csv("D:/PythonProjects/shiny-waffle/tests/time_series_test.csv", "%Y-%m-%d")
equinor.add_time_series("financial_report", financial_reports)
equinor.set_bars(equinor_bars, "daily")
sma_strategy.link_stock(equinor)

backtester = Backtester(portfolio, ib, [equinor], [sma_strategy], "daily")
backtester.run()
