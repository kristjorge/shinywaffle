import os
from datetime import datetime
from tools.alpha_vantage import AlphaVantage
from backtesting.backtest import Backtester
from financial_assets.financial_assets import Stock
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from strategy.sma_crossover import AverageCrossOver
from backtesting.workflow.backtest_workflow import BacktestWorkflow


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

backtester = Backtester(portfolio, ib, [equinor], "daily", run_to=datetime(2020, 1, 1))
workflow = BacktestWorkflow(backtester, "Simple SMA on Apple and Microsoft", path="D:/PythonProjects/shiny-waffle/backtesting/runs",
                            runs=5, sub_runs=5, out_of_sample_size=0.2, wfa='anchored', stochastic_runs=3)

workflow.set_uncertainty_parameter_values("D:/PythonProjects/shiny-waffle/tests/parameters.csv")
workflow.run()


