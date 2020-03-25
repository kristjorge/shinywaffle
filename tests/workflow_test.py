import os
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from financial_assets.financial_assets import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from backtesting.workflow.backtest_workflow import BacktestWorkflow
from strategy.sma_crossover import AverageCrossOver
from backtesting.workflow.uncertainty_variable import UncertaintyVariable
from data.time_series_data import TimeSeriesDataReader

portfolio = Portfolio(500, "USD")
ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver("SMA crossover", short=UncertaintyVariable("short"), long=UncertaintyVariable("long"))


# Equinor stocks
equinor = Stock("Equinor Energy", "EQNR", "USD")
equinor_bars = alpha_vantage.query("TIME_SERIES_DAILY", "EQNR", reverse=True)
financial_reports = TimeSeriesDataReader().read_csv("D:/PythonProjects/shiny-waffle/tests/time_series_test.csv", "daily")
equinor.add_data_series("financial_report", financial_reports)
equinor.set_bars(equinor_bars)
sma_strategy.link(equinor)

backtester = Backtester(portfolio, ib, [equinor], [sma_strategy], "daily")
workflow = BacktestWorkflow(backtester, "Simple SMA on Apple and Microsoft", path="D:/PythonProjects/shiny-waffle/backtesting/runs",
                            runs=5, sub_runs=5, out_of_sample_size=0.2, wfa='anchored', stochastic_runs=3)

workflow.set_uncertainty_parameter_values("D:/PythonProjects/shiny-waffle/tests/parameters.csv")
workflow.run()


