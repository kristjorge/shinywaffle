from common.event import events
from backtesting.tradelog import TradeLog
from common.positions.position_container import PositionContainer
from common.positions.position import Position
from common.context import Context
from backtesting import orders


class Account:

    """

    Class holding the initial holding in a base currency for the backtesting

    """

    # TODO: Implement round down method

    def __init__(self, context: Context, initial_holding: float, base_asset):
        self.initial_holding = initial_holding
        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_asset = base_asset
        self.assets = {asset.ticker: {'holding': 0, 'value': 0, 'asset_data': asset} for asset in context.assets.values()}
        self.time_series = {
            'total value': [],
            'cash': [],
            'number of active positions': []
        }
        self.trade_log = TradeLog()
        self.times_readable = []
        self.times = []
        self.risk_manager = None
        self.broker = context.broker
        self.context = context
        context.account = self
        self.positions = PositionContainer(context)

        try:
            self.risk_manager = context.risk_manager
        except AttributeError:
            pass

        try:
            context.risk_manager.account = self
        except AttributeError:
            pass

    def debit(self, amount: float):
        self.cash += amount

    def credit(self, amount: float):
        self.cash -= amount

    def place_buy_order(self, event):
        new_order = None
        if event.order_volume > 0:
            time_placed = self.context.retrieved_data.time
            if type(event) == events.SignalEventMarketBuy:
                new_order = orders.MarketBuyOrder(event.asset,
                                                  event.order_volume,
                                                  time_placed)

            elif type(event) == events.SignalEventLimitBuy:
                new_order = orders.LimitBuyOrder(event.asset,
                                                 event.order_volume,
                                                 event.order_limit_price,
                                                 time_placed)

            pending_order_event = self.broker.place_order(new_order)
            return pending_order_event

        else:
            return None

    def place_sell_order(self, event):
        max_vol = self.assets[event.asset.ticker]['holding']
        time_placed = self.context.retrieved_data.time
        order_volume = min(max_vol, event.order_volume)
        new_order = None
        if order_volume > 0:

            if type(event) == events.SignalEventMarketSell:
                new_order = orders.MarketSellOrder(event.asset,
                                                   order_volume,
                                                   time_placed)

            elif type(event) == events.SignalEventLimitSell:
                new_order = orders.LimitSellOrder(event.asset,
                                                  order_volume,
                                                  event.order_limit_price,
                                                  time_placed)

            pending_order_event = self.broker.place_order(new_order)
            return pending_order_event

        else:
            return None

    def complete_order(self, event):
        """
        Method to register a filled order from the broker on the account.
        This method logs a trade with the self.trade_log

        If the event.type == 'buy' then
                1) a new position in the position container is established
                2) Increment the holding for the respective asset
                3) Decrement the cash is decremented equal to the transaction amount
                4) Decrement the cash the amount for the commission

        If the event.type == 'sell' then
                1) Call 'sell_off_position' from the position container
                2) Decrement the holding for the respective asset
                3) Increment the cash equal to the transaction amount
                4) Decrement the cash the amount for the commission
        :param event:
        :return:
        """

        self.trade_log.new_trade(event.asset, event.order_size,
                                 event.price, event.order_volume,
                                 event.type, event.time, event.commission)

        if event.side == 'buy':
            position = Position(event.time,
                                event.asset,
                                event.order_volume,
                                event.order_size,
                                event.price)

            self.positions.enter_position(position)
            self.assets[event.asset.ticker]['holding'] += event.order_volume
            self.credit(event.order_size)
            self.credit(event.commission)

        elif event.side == 'sell':
            self.positions.sell_off_position(event.asset.ticker,
                                             event.order_volume,
                                             event.price,
                                             event.time)

            self.assets[event.asset.ticker]['holding'] -= event.order_volume
            self.debit(event.order_size)
            self.credit(event.commission)

    def update(self):
        """
        Update various values for the account object:
            - Total value
            - Cash
            - Report times
            - Various position tracking functionalities
        :return:
        """
        total_value = self.cash
        for ticker, asset in self.assets.items():
            asset['asset_data'].latest_bar = self.context.retrieved_data[ticker]['bars'][0]
            try:
                asset['value'] = asset['holding'] * asset['asset_data'].latest_bar.close
            except TypeError:
                # Catching None
                asset['value'] = 0
            finally:
                total_value += asset['value']

        self.times.append(self.context.retrieved_data.time)
        self.times_readable.append(self.context.retrieved_data.time.strftime('%d-%m-%Y %H:%M:%S'))
        self.total_value = total_value
        self.time_series['total value'].append(total_value)
        self.time_series['cash'].append(self.cash)
        self.time_series['number of active positions'].append(self.trade_log.active_trades)
        self.positions.update_positions()

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
