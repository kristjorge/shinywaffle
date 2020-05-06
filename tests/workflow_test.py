from backtesting.workflow.workflow import BacktestWorkflow
from backtesting.workflow.uncertainty_variable import UncertaintyVariable
from datetime import datetime
from data.bar_provider import BarProvider
from backtesting.backtest import Backtester
from risk.risk_management import BaseRiskManager
from common.assets import assets
from common.account import Account
from backtesting.broker import BacktestBroker
from strategy import sma_crossover
from common.context import Context

context = Context()

broker = BacktestBroker(context, 0.)
trading_strategy = sma_crossover.AverageCrossOver(context=context,
                                                  short=UncertaintyVariable('short'),
                                                  long=UncertaintyVariable('long'))


# Nvidia stocks
nvidia = assets.Stock(context, "Nvidia", "NVDA", assets.USD())
nvidia_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/NVDA_1D.csv', '%Y-%m-%d')
nvidia.set_bars(nvidia_bars)

# Oracle stocks
oracle = assets.Stock(context, "Oracle", "ORCL", assets.USD())
oracle_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/ORCL_1D.csv', '%Y-%m-%d')
oracle.set_bars(oracle_bars)

# IBM stocks
ibm = assets.Stock(context, "IBM", "IBM", assets.USD())
ibm_bars = BarProvider('D:/PythonProjects/shiny-waffle/data/yahoo_finance/IBM_1D.csv', '%Y-%m-%d')
ibm.set_bars(ibm_bars)

trading_strategy.apply_to_asset(nvidia, oracle, ibm)

risk_manager = BaseRiskManager(context)
account = Account(context, 1000, assets.USD())
backtester = Backtester(context, 'daily', run_from=datetime(2011, 1, 1), run_to=datetime(2020, 1, 1))
workflow = BacktestWorkflow(context, backtester, "Simple SMA workflow sample ",
                            path="D:/PythonProjects/shiny-waffle/backtesting/runs",
                            runs=1, sub_runs=1, out_of_sample_size=0.2, wfa='anchored', stochastic_runs=2)

workflow.set_uncertainty_parameter_values("D:/PythonProjects/shiny-waffle/tests/parameters.csv")
workflow.run()


