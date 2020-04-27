from tools.binance import BinancePublic
from common.financial_assets import financial_assets
from backtesting.account import Account
from backtesting.brokers import Binance
from strategy.random_signal_strategy import RandomSignalStrategy
from data.data_provider import LiveDataProvider
from backtesting.risk_management import BaseRiskManager
from common.event.event_handler import EventHandler


binance_broker = Binance()
binance_api = BinancePublic()
sma_strategy = RandomSignalStrategy("Random strategy")


ether = financial_assets.Cryptocurrency("Ethereum", "ETH", "BTC")
ether_bars = binance_api.get_candlesticks("BTC", "ETH", "1m", return_as_link=True)
ether.set_bars(ether_bars)
ether.add_strategy(sma_strategy)
portfolio = Account(1, "BTC", [ether])
risk_manager = BaseRiskManager(portfolio)
portfolio.set_risk_manager(risk_manager)
data_provider = LiveDataProvider({'ETH': ether}, sleep_time=10)
event_handler = EventHandler(portfolio, binance_broker, {'ETH': ether}, data_provider)
