import os
from datetime import datetime
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from financial_assets.financial_assets import Stock
from backtesting.account import Account
from backtesting.brokers import InteractiveBrokers
from strategy.sma_crossover import AverageCrossOver
from backtesting.workflow.backtest_workflow import BacktestWorkflow
from backtesting.workflow.uncertainty_variable import UncertaintyVariable
from backtesting.risk_management import RiskManager


ib = InteractiveBrokers()
alpha_vantage = AlphaVantage(os.environ['AlphaVantage_APItoken'])
sma_strategy = AverageCrossOver("SMA crossover", short=UncertaintyVariable("short"), long=UncertaintyVariable("long"))


# Equinor stocks
equinor = Stock("Equinor Energy", "EQNR", "USD")
equinor_bars = alpha_vantage.query_stocks("TIME_SERIES_DAILY", "EQNR", outputsize="full")

equinor.set_bars(equinor_bars)
equinor.add_strategy(sma_strategy)

portfolio = Account(500, "USD", [equinor], RiskManager())

backtester = Backtester(portfolio, ib, [equinor], "daily", run_to=datetime(2020, 1, 1))
workflow = BacktestWorkflow(backtester, "Simple SMA on Equinor ", path="D:/PythonProjects/shiny-waffle/backtesting/runs",
                            runs=3, sub_runs=1, out_of_sample_size=0.2, wfa='anchored', stochastic_runs=1)

workflow.set_uncertainty_parameter_values("D:/PythonProjects/shiny-waffle/tests/parameters.csv")
workflow.run()


