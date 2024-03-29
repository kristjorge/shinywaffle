from __future__ import annotations
from shinywaffle.common.event import events
from shinywaffle.backtesting.tradelog import TradeLog
from shinywaffle.common.position import PositionContainer
from shinywaffle.common.context import Context
from shinywaffle.backtesting import orders
from shinywaffle.backtesting.orders import OrderSide, PendingOrderEvent
from shinywaffle.common.assets import Asset, BaseAsset
from shinywaffle.common.metrics import drawdown
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from shinywaffle.risk.risk_management import RiskManager


class BaseAssetBalance:
    def __init__(self, base_asset: BaseAsset, context: Context, initial_balance: float = 0):
        self.base_asset = base_asset
        self.context = context
        self.balance = initial_balance

    def deposit(self, amount: float):
        """ increase base asset balance """
        self.balance += amount

    def withdraw(self, amount: float):
        """ decrease base asset balance """
        self.balance -= amount


class AssetBalance:
    def __init__(self, asset: Asset, context: Context, initial_balance: float = 0):
        """ Balance entry of an asset in the account. Holds the information of the balance and the latest value"""
        self.asset = asset
        self.context = context
        self.balance = initial_balance

    def add_to_balance(self, volume: Union[float, int]):
        """ Increase balance """
        self.balance += volume

    def deduct_from_balance(self, volume: Union[float, int]):
        """ Decrease balance """
        self.balance -= volume

    @property
    def value(self):
        """ The value of the balance"""
        return self.balance * self.asset.bars[0].close


class Account:

    """
    Class holding the initial holding in a base currency for the backtesting
    """

    # TODO: Implement round down method

    def __init__(self, context: Context, base_asset: BaseAsset, risk_manager: RiskManager):
        self.initial_holding = base_asset.initial_balance
        self.base_balance = BaseAssetBalance(context=context, base_asset=base_asset, initial_balance=base_asset.initial_balance)
        self.positions = {asset: PositionContainer(context=context, asset=asset) for asset in context.assets.values()}
        self.balances = {asset: AssetBalance(asset=asset, context=context) for asset in context.assets.values()}

        self.time_series = {
            'values': [],
            'returns': [],
            'returns_percent': [],
            'base_balances': [],
            'balances': {asset.ticker: [] for asset in self.balances.keys()},
            'number of active positions': []
        }

        self.trade_log = TradeLog()
        self.risk_manager = risk_manager
        self.context = context

    def deposit(self, amount: float):
        """ Debit an amount into the account"""
        self.base_balance.deposit(amount=amount)

    def withdraw(self, amount: float):
        """ Credit an amount from the account"""
        self.base_balance.withdraw(amount=amount)

    def place_buy_order(self, event: Union[events.SignalEventLimitBuy, events.SignalEventMarketBuy]) -> Union[None, PendingOrderEvent]:
        """
        Processes a signal to place a buy order in the form of either a market or limit order.

        Returns a PendingOrder object to be handled by the event handler.
        """
        new_order = self.handle_buy_order_event(event=event)
        pending_order_event = self.context.broker.place_order(new_order)
        stop_loss = self.risk_manager.stop_loss_exit(asset=event.asset)
        trailing_stop = self.risk_manager.trailing_stop_exit(asset=event.asset)
        target_exit = self.risk_manager.target_exit(asset=event.asset)

        return pending_order_event

    def place_sell_order(self, event: Union[events.SignalEventMarketSell, events.SignalEventLimitSell]) -> Union[None, PendingOrderEvent]:
        """
        Processes a signal to place a sell order in the form of either a market or limit order. Max volume to sell
        is the entire balance of an asset in the account.

        Returns a PendingOrder object to be handled by the event handler.
        """
        new_order = self.handle_sell_order_event(event=event)
        pending_order_event = self.context.broker.place_order(new_order)
        return pending_order_event

    def complete_order(self, event: events.OrderFilledEvent) -> None:
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

        self.trade_log.new_trade(asset=event.asset, trade_size=event.order_size,
                                 fill_price=event.filled_price, order_price=event.order_price,
                                 trade_volume=event.order_volume, trade_type=event.type,
                                 trade_side=event.side, timestamp=event.time, commission=event.commission)

        if event.side == OrderSide.BUY:
            self.positions[event.asset].enter_position(time=event.time,
                                                       volume=event.order_volume,
                                                       size=event.order_size,
                                                       price=event.filled_price)
            self.withdraw(event.order_size)
            self.withdraw(event.commission)
            self.balances[event.asset].add_to_balance(volume=event.order_volume)

        elif event.side == OrderSide.SELL:
            self.positions[event.asset].sell_off(volume=event.order_volume,
                                                 price=event.filled_price,
                                                 time=event.time)

            self.deposit(event.order_size)
            self.withdraw(event.commission)
            self.balances[event.asset].deduct_from_balance(volume=event.order_volume)

    def handle_buy_order_event(self, event: Union[events.SignalEventLimitBuy, events.SignalEventMarketBuy]) -> Union[orders.MarketBuyOrder, orders.LimitBuyOrder]:
        """ Returns a MarketBuyOrder or LimitBuyOrder depending on the signal received"""
        time_placed = self.context.time
        order_volume = self.risk_manager.position_size_entry(asset=event.asset)
        if isinstance(event, events.SignalEventMarketBuy):
            new_order = orders.MarketBuyOrder(asset=event.asset,
                                              volume=order_volume,
                                              time=time_placed,
                                              expires_at=event.expires_at)

        elif isinstance(event, events.SignalEventLimitBuy):
            new_order = orders.LimitBuyOrder(asset=event.asset,
                                             volume=order_volume,
                                             limit_price=event.order_limit_price,
                                             time=time_placed,
                                             expires_at=event.expires_at)
        else:
            raise TypeError('Provided buy order event is not of type SignalEventMarketBuy or SignalEventLimitBuy')

        return new_order

    def handle_sell_order_event(self, event: Union[events.SignalEventMarketSell, events.SignalEventLimitSell]) -> Union[orders.MarketSellOrder, orders.LimitSellOrder]:
        """ Returning a MarketSellOrder or LimitSellOrder depending on the signal received"""
        time_placed = self.context.time
        order_volume = self.risk_manager.position_size_exit(asset=event.asset)

        # Cap the order volume to the asset balance
        if order_volume > self.balances[event.asset].balance:
            order_volume = self.balances[event.asset].balance

        if isinstance(event, events.SignalEventMarketSell):
            new_order = orders.MarketSellOrder(asset=event.asset,
                                               volume=order_volume,
                                               time=time_placed,
                                               expires_at=event.expires_at)

        elif isinstance(event, events.SignalEventLimitSell):
            new_order = orders.LimitSellOrder(asset=event.asset,
                                              volume=order_volume,
                                              limit_price=event.order_limit_price,
                                              time=time_placed,
                                              expires_at=event.expires_at)
        else:
            raise TypeError('Provided sell order event is not of type MarketSellOrder or LimitSellOrder')

        return new_order

    @property
    def value(self) -> float:
        """ Total value of the account including all balances and the cash on hand. """
        total_value = self.base_balance.balance
        for balance in self.balances.values():
            total_value += balance.value

        return total_value

    def update(self):
        """
        Update various values for the account object:
            - Total value
            - Cash
            - Report times
            - Various position tracking functionalities
        """

        returns = self.value - self.initial_holding
        returns_percent = returns / self.initial_holding

        self.time_series['values'].append(self.value)
        self.time_series['base_balances'].append(self.base_balance.balance)
        self.time_series['returns'].append(returns)
        self.time_series['returns_percent'].append(returns_percent)

        for asset in self.balances.keys():
            self.time_series['balances'][asset.ticker].append(self.balances[asset].balance)

        for position_container in self.positions.values():
            position_container.update_position()

    def report(self):
        num_winning = sum([pos.num_winning_positions for pos in self.positions.values()])
        num_losing = sum([pos.num_losing_positions for pos in self.positions.values()])
        tot_win_return = sum([pos.tot_win_pos_return for pos in self.positions.values()])
        tot_los_return = sum([pos.tot_los_pos_return for pos in self.positions.values()])
        tot_win_return_percent = sum([pos.tot_win_pos_return_percent for pos in self.positions.values()])
        tot_los_return_percent = sum([pos.tot_los_pos_return_percent for pos in self.positions.values()])

        try:
            avg_win_return = tot_win_return / num_winning
        except ZeroDivisionError:
            avg_win_return = 0.

        try:
            avg_los_return = tot_los_return / num_losing
        except ZeroDivisionError:
            avg_los_return = 0.

        try:
            avg_win_return_percent = tot_win_return_percent / num_winning
        except ZeroDivisionError:
            avg_win_return_percent = 0.

        try:
            avg_los_return_percent = tot_los_return_percent / num_losing
        except ZeroDivisionError:
            avg_los_return_percent = 0.

        try:
            frac_winning = num_winning / (num_winning + num_losing)
        except ZeroDivisionError:
            frac_winning = 0.

        data = {
            'trades': self.trade_log.report(),
            'values': self.time_series['values'],
            'return': self.time_series['returns'][-1],
            'return_percent': self.time_series['returns_percent'][-1],
            'returns': self.time_series['returns'],
            'returns_percent': self.time_series['returns_percent'],
            'maximum_drawdown': drawdown(values=self.time_series['values']),
            'base_balances': self.time_series['base_balances'],
            'active_trades': self.time_series['number of active positions'],
            'balances': self.time_series['balances'],
            'positions': {asset.ticker: pos.report() for asset, pos in self.positions.items()},
            'num_winning_positions': num_winning,
            'num_losing_positions': num_losing,
            'frac_winning': frac_winning,
            'avg_win_return': avg_win_return,
            'avg_los_return': avg_los_return,
            'avg_win_return_percent': avg_win_return_percent,
            'avg_los_return_percent': avg_los_return_percent
        }

        return data
