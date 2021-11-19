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
import numpy as np


np.random.seed(seed=0)


def main():
    context = Context()

    time_increment = '2h'
    time_from = datetime(2019, 1, 1, 0, 0, 0)
    time_to = datetime(2021, 1, 1, 0, 0, 0)

    backtest_from = datetime(2019, 2, 1)
    backtest_to = datetime(2020, 1, 1)

    broker = BacktestBroker(context=context, fee=0., fee_fixed=0.)
    trading_strategy = sma_crossover.AverageCrossOver(context=context, short=15, long=40)

    # USDT
    usdt = assets.USDT(initial_balance=500.00)

    # Bitcoin cryptocurrency
    bitcoin = assets.Cryptocurrency(context=context, name="Bitcoin", ticker="BTC")
    bitcoin_bars = BinancePublic().get_candlesticks(base_asset='USDT',
                                                    quote_asset='BTC',
                                                    interval=time_increment,
                                                    time_from=time_from,
                                                    time_to=time_to)

    #ether_bars = BinancePublic().get_candlesticks(base_asset='USDT',
    #                                              quote_asset='ETH',
    #                                              interval=time_increment,
    #                                              time_from=time_from,
    #                                              time_to=time_to)

    context.save_time_series(asset=bitcoin, time_series=bitcoin_bars, series_type=TimeSeriesType.TYPE_ASSET_BARS)
    #context.save_time_series(asset=bitcoin, time_series=ether_bars, series_type=TimeSeriesType.TYPE_ASSOCIATED_BARS)
    trading_strategy.apply_to_asset(bitcoin)

    risk_manager = BaseRiskManager(context=context)
    account = Account(context=context, base_asset=usdt, risk_manager=risk_manager)
    context.set_broker(broker=broker)
    context.set_account(account=account)
    backtester = Backtester(context=context, time_increment=time_increment, run_from=backtest_from, run_to=backtest_to)
    backtester.run()


if __name__ == '__main__':
    main()