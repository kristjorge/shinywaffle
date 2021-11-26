from datetime import datetime

from shinywaffle.data.time_series_data import TimeSeriesType
from shinywaffle.backtesting.backtest import Backtester
from shinywaffle.risk.risk_management import BaseRiskManager
from shinywaffle.common import assets
from shinywaffle.common.account import Account
from shinywaffle.common.broker import BacktestBroker
from shinywaffle.strategy import sma_crossover
from shinywaffle.common.context import Context
from shinywaffle.tools.binance import BinancePublic
from shinywaffle.backtesting.study.study import BacktestStudy
from shinywaffle.backtesting.study.uncertainy import UncertaintyVariableSwappable, UncertaintyVariableManifest
from shinywaffle.backtesting.study.study import TypeWFA


def main():
    context = Context()

    time_increment = '2h'
    time_from = datetime(2018, 1, 1, 0, 0, 0)
    time_to = datetime(2021, 5, 1, 0, 0, 0)

    backtest_from = datetime(2019, 2, 1)
    backtest_to = datetime(2020, 1, 1)

    broker = BacktestBroker(context=context, fee=0.001)

    trading_strategy = sma_crossover.AverageCrossOver(context=context,
                                                      short=1,
                                                      long=1)

    # USDT
    usdt = assets.USDT(initial_balance=500.00)

    # Bitcoin cryptocurrency
    bitcoin = assets.Cryptocurrency(context=context, name="Bitcoin", ticker="BTC")
    bitcoin_bars = BinancePublic().get_candlesticks(base_asset='USDT',
                                                    quote_asset='BTC',
                                                    interval=time_increment,
                                                    time_from=time_from,
                                                    time_to=time_to)

    context.save_time_series(asset=bitcoin, time_series=bitcoin_bars, series_type=TimeSeriesType.TYPE_ASSET_BARS)
    trading_strategy.apply_to_asset(bitcoin)

    risk_manager = BaseRiskManager(context=context)
    account = Account(context=context, base_asset=usdt, risk_manager=risk_manager)
    context.set_broker(broker=broker)
    context.set_account(account=account)

    swappable_sma_short = UncertaintyVariableSwappable(parent_obj=trading_strategy,
                                                       attr_name='short',
                                                       name='sma_short')

    swappable_sma_long = UncertaintyVariableSwappable(parent_obj=trading_strategy,
                                                      attr_name='long',
                                                      name='sma_long')

    swappable_manifest = UncertaintyVariableManifest()
    swappable_manifest.add_swappable(swappable=[swappable_sma_long, swappable_sma_short])

    backtester = Backtester(context=context, time_increment=time_increment, run_from=backtest_from, run_to=backtest_to)
    study = BacktestStudy(context=context, backtester=backtester, study_name="Simple SMA study sample ",
                          save_path="C:/PythonProjects/shiny-waffle/simulations/",
                          num_runs=2, num_sub_runs=2, out_of_sample_size=0.2,
                          wfa=TypeWFA.ANCHORED, num_stochastic_runs=2, variable_swap_manifest=swappable_manifest)

    study.set_uncertainty_parameter_values("C:/PythonProjects/shiny-waffle/tests/parameters.csv")
    study.run()


if __name__ == '__main__':
    main()