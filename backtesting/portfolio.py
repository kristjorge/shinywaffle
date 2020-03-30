from backtesting import risk_management
from event import events
from backtesting.trades import Trades


class Portfolio:

    """

    Class holding the initial holding in a base currency for the backtesting

    """

    available_currencies = ("USD", "NOK", "GBP", "EUR")

    def __init__(self, initial_holding, currency, assets, risk_manager):
        assert isinstance(assets, list)
        assert isinstance(risk_manager, risk_management.RiskManager)
        assert currency in Portfolio.available_currencies

        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_currency = currency
        self.assets = {asset.ticker: {'holding': 0, 'value': 0, 'asset_data': asset} for asset in assets}
        self.times = []
        self.running_total_value = []
        self.running_cash = []
        self.times_readable = []
        self.risk_manager = risk_manager

    def debit(self, amount):
        self.cash += amount

    def credit(self, amount):
        self.cash -= amount

    @ staticmethod
    def place_order(asset, order_size, order_type, price=None):
        # TODO: Add a check to see if there are available assets to sell.
        # TODO: Limit the order volume to the number of assets currently in holding
        if price is None:
            event = events.MarketOrderEvent(asset, order_size, order_type)
        else:
            # If the price is specified, return a limit order type event
            event = events.LimitOrderEvent(asset, order_size, price, order_type)
        return event

    @ staticmethod
    def place_buy_order(asset, order_size, price=None):
        if price is None:
            event = events.MarketOrderBuyEvent(asset, order_size)
        else:
            # If the price is specified, return a limit order type event
            event = events.LimitOrderBuyEvent(asset, order_size, price)
        return event

    def place_sell_order(self, asset, order_size, price=None):
        # TODO: Add a check to see if there are available assets to sell.
        # TODO: Limit the order volume to the number of assets currently in holding
        max_volume = self.assets[asset.ticker]['holding']
        if price is None:
            event = events.MarketOrderSellEvent(asset, order_size, max_volume)
        else:
            # If the price is specified, return a limit order type event
            event = events.LimitOrderSellEvent(asset, order_size, price, max_volume)
        return event

    def register_order(self, order_event):

        Trades(order_event.asset, order_event.order_size, order_event.price, order_event.order_volume, order_event.type)

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
                total_value += asset['value']

        self.times.append(time_series_data['times'])
        self.times_readable.append(time_series_data['times'].strftime('%d-%m-%Y %H:%M:%S'))
        self.total_value = total_value
        self.running_total_value.append(total_value)
        self.running_cash.append(self.cash)

    def self2dict(self):
        data = {
            'trades': Trades.self2dict(),
            'times': self.times_readable,
            'total value': self.running_total_value,
            'cash': self.running_cash
        }

        return data

    @property
    def value_over_time(self):
        return [(t.strftime("%d-%m-%Y %H:%M:%S"), v) for (t, v) in zip(self.times, self.total_value)]
