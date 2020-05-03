from tools.binance import BinancePublic
from common.assets import assets
from common.account import Account
from backtesting.broker import Binance
from strategy.random_signal_strategy import FixedDatesTransactionsStrategy
from data.data_provider import LiveDataProvider
from risk.risk_management import BaseRiskManager
from common.event.event_handler import EventHandler


binance_broker = Binance()
binance_api = BinancePublic()
sma_strategy = FixedDatesTransactionsStrategy("Random strategy")


ether = assets.Cryptocurrency("Ethereum", "ETH", "BTC")
ether_bars = binance_api.get_candlesticks("BTC", "ETH", "1m", return_as_link=True)
ether.set_bars(ether_bars)
ether.add_strategy(sma_strategy)
portfolio = Account(1, "BTC", [ether])
risk_manager = BaseRiskManager(portfolio)
portfolio.set_risk_manager(risk_manager)
data_provider = LiveDataProvider({'ETH': ether}, sleep_time=10)
event_handler = EventHandler(portfolio, binance_broker, {'ETH': ether}, data_provider)
