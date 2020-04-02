from backtesting import risk_management
from event import events
from backtesting.trades import Trades


class Portfolio:

    """

    Class holding the initial holding in a base currency for the backtesting

    """

    # TODO: Enable position tracking and partial sell of from positions. Needs to be in place to calculate trade profitability

    available_currencies = ("USD", "NOK", "GBP", "EUR")

    def __init__(self, initial_holding, currency, assets, risk_manager):
        assert isinstance(assets, list)
        assert isinstance(risk_manager, risk_management.RiskManager)
        assert currency in Portfolio.available_currencies

        self.initial_holding = initial_holding
        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_currency = currency
        self.assets = {asset.ticker: {'holding': 0, 'value': 0, 'asset_data': asset} for asset in assets}
        self.times = []
        self.time_series = {
            'total value': [],
            'cash': [],
            'number of active positions': []
        }
        self.trades = Trades()
        self.times_readable = []
        self.risk_manager = risk_manager

    def debit(self, amount):
        self.cash += amount

    def credit(self, amount):
        self.cash -= amount

    @ staticmethod
    def place_buy_order(asset, order_size, price=None):
        if price is None:
            event = events.MarketOrderBuyEvent(asset, order_size)
        else:
            event = events.LimitOrderBuyEvent(asset, order_size, price)
        return event

    def place_sell_order(self, asset, order_size, price=None):
        max_volume = self.assets[asset.ticker]['holding']
        if price is None:
            event = events.MarketOrderSellEvent(asset, order_size, max_volume)
        else:
            event = events.LimitOrderSellEvent(asset, order_size, price, max_volume)
        return event

    def register_order(self, order_event, timestamp):

        self.trades.new_trade(order_event.asset, order_event.order_size,
                              order_event.price, order_event.order_volume,
                              order_event.type, timestamp)

        if order_event.type == 'buy':
            self.assets[order_event.asset.ticker]['holding'] += order_event.order_volume
            self.credit(order_event.order_size)
        elif order_event.type == 'sell':
            self.assets[order_event.asset.ticker]['holding'] -= order_event.order_volume
            self.debit(order_event.order_size)

    def update_portfolio(self, time_series_data):

        total_value = self.cash

        for ticker, asset in self.assets.items():
            if ticker in time_series_data:
                asset['asset_data'].latest_bar = time_series_data[ticker]['bars'][0]
                try:
                    asset['value'] = asset['holding'] * asset['asset_data'].latest_bar.close
                except TypeError:
                    # Catching None
                    asset['value'] = 0
                finally:
                    total_value += asset['value']

        self.times.append(time_series_data['current time'])
        self.times_readable.append(time_series_data['current time'].strftime('%d-%m-%Y %H:%M:%S'))
        self.total_value = total_value
        self.time_series['total value'].append(total_value)
        self.time_series['cash'].append(self.cash)
        self.time_series['number of active positions'].append(self.trades.active_trades)

    def self2dict(self):
        data = {
            'trades': self.trades.self2dict(),
            'times': self.times_readable,
            'total value': self.time_series['total value'],
            'cash': self.time_series['cash'],
            'active trades': self.time_series['number of active positions']
        }

        return data
