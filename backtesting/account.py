from event import events
from backtesting.tradelog import TradeLog
from positions.position_container import PositionContainer
from positions.position import Position


class Account:

    """

    Class holding the initial holding in a base currency for the backtesting

    """

    # TODO: Implement round half down method

    def __init__(self, initial_holding, currency, assets, num_base_decimals=2):
        self.initial_holding = initial_holding
        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_currency = currency
        self.base_currency_decimals = num_base_decimals
        self.assets = {asset.ticker: {'holding': 0, 'value': 0, 'asset_data': asset} for asset in assets}
        self.times = []
        self.time_series = {
            'total value': [],
            'cash': [],
            'number of active positions': []
        }
        self.trade_log = TradeLog()
        self.times_readable = []
        self.risk_manager = None
        self.positions = PositionContainer(self.assets, self)

    def debit(self, amount):
        self.cash += amount

    def credit(self, amount):
        self.cash -= amount

    def set_risk_manager(self, risk_manager):
        self.risk_manager = risk_manager

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

    def register_order(self, event, timestamp):
        """
        Method to register a filled order from the broker on the portfolio.
        This method logs a trade with the self.trade_log

        If the event.type == 'buy' then
                1) a new position in the position container is established
                2) Increment the holding for the respective asset
                3) Decrement the cash is decremented equal to the transaction amount
                4) Decrement the cash the amount for the commission

        IF the event.type == 'sell' then
                1) Call 'sell_off_position' from the position container
                2) Decrement the holding for the respective asset
                3) Increment the cash equal to the transaction amount
                4) Decrement the cash the amount for the commission
        :param event:
        :param timestamp:
        :return:
        """
        print('registering order')
        self.trade_log.new_trade(event.asset, event.order_size,
                                 event.price, event.order_volume,
                                 event.type, timestamp, event.commission)

        if event.type == 'buy':
            position = Position(timestamp, event.asset, event.order_volume,
                                event.order_size, event.price)

            self.positions.enter_position(position)
            self.assets[event.asset.ticker]['holding'] += event.order_volume
            self.credit(event.order_size)
            self.credit(event.commission)
        elif event.type == 'sell':
            self.positions.sell_off_position(event.asset.ticker, event.order_volume, event.price, timestamp)
            self.assets[event.asset.ticker]['holding'] -= event.order_volume
            self.debit(event.order_size)
            self.credit(event.commission)

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
        self.time_series['number of active positions'].append(self.trade_log.active_trades)
        self.positions.update_positions(time_series_data)

    def self2dict(self):
        data = {
            'trades': self.trade_log.self2dict(),
            'times': self.times_readable,
            'total value': self.time_series['total value'],
            'cash': self.time_series['cash'],
            'active trades': self.time_series['number of active positions'],
            'positions': self.positions.report()
        }

        return data