import os
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from backtesting.stock.stock import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from backtesting.workflow.backtest_workflow import BacktestWorkflow
from strategy.sma_crossover import AverageCrossOver
from backtesting.workflow.uncertainty_variable import UncertaintyVariable
from utils.time_series_data import TimeSeriesDataReader

portfolio = Portfolio(500, "USD")
ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])

# Equinor stocks
equinor = Stock("Equinor Energy", "EQNR")
equinor.add_strategy(AverageCrossOver("SMA crossover", short=UncertaintyVariable("short"), long=UncertaintyVariable("long")))
equinor_bars = alpha_vantage.query("TIME_SERIES_DAILY_ADJUSTED", "EQNR", output_as_bars=True, reverse=True)
# financial_reports = TimeSeriesDataReader().read_csv("D:/PythonProjects/shiny-waffle/tests/time_series_test.csv", "%Y-%m-%d")
# equinor.add_time_series("financial_report", financial_reports)
equinor.set_bars(equinor_bars, "daily")

backtester = Backtester(portfolio, ib, [equinor], "daily")
workflow = BacktestWorkflow(backtester, "Simple SMA on Apple and Microsoft", path="//Backtesting/runs",
                            runs=5, sub_runs=5, out_of_sample_size=0.2, wfa='anchored', stochastic_runs=3)

workflow.set_uncertainty_parameter_values("D:/PythonProjects/shiny-waffle/tests/parameters.csv")
workflow.run()


