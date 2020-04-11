from tools.binance import BinancePublic
from financial_assets import financial_assets
from backtesting.portfolio import Portfolio
from backtesting.broker.brokers import InteractiveBrokers
from strategy.random_signal_strategy import RandomSignalStrategy
from data.data_provider import LiveDataProvider
from backtesting.risk_management import RiskManager
from event.event_handler import EventHandler


ib = InteractiveBrokers()
binance = BinancePublic()
sma_strategy = RandomSignalStrategy("Random strategy")


ether = financial_assets.Cryptocurrency("Ethereum", "ETH", "BTC")
ether_bars = binance.get_candlesticks("BTC", "ETH", "1m", return_as_link=True)
ether.set_bars(ether_bars)
ether.add_strategy(sma_strategy)
portfolio = Portfolio(1, "BTC", [ether])
risk_manager = RiskManager(portfolio)
portfolio.set_risk_manager(risk_manager)
data_provider = LiveDataProvider({'ETH': ether}, sleep_time=10)
event_handler = EventHandler(portfolio, ib, {'ETH': ether}, data_provider)
