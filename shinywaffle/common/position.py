from datetime import datetime
from shinywaffle.common.context import Context
from shinywaffle.common.assets import Asset
from shinywaffle.backtesting.orders import OrderSide
from typing import Union, Tuple, List
from shinywaffle.common.metrics import drawdown


class ShareCount:
    def __init__(self, num_shares: Union[int, float], price: float):
        self.num_shares = num_shares
        self.price = price

    def sell_off(self, num_shares: Union[int, float]) -> Tuple[Union[int, float], Union[int, float]]:
        num_sell_off = min(num_shares, self.num_shares)
        self.num_shares -= num_sell_off
        remaining_to_sell = num_shares - num_sell_off
        return self.num_shares, remaining_to_sell

    def __repr__(self):
        return f'{self.num_shares} shares at {self.price}'


class SharesCounter:
    def __init__(self):
        self.share_counts = list()

    def add_share_count(self, share_count: ShareCount):
        self.share_counts.append(share_count)

    def sell_off(self, num_shares: Union[int, float]) -> Union[int, float]:
        while num_shares > 0 and self.share_counts:
            num_rem_at_price, num_shares = self.share_counts[0].sell_off(num_shares=num_shares)
            if num_rem_at_price == 0:
                _ = self.share_counts.pop(0)

        return num_shares


class Transaction:
    def __init__(self, volume: Union[float, int], price: float, side: OrderSide, time: datetime):
        """ A transaction on a position"""
        self.volume = volume
        self.price = price
        self.size = volume * price
        self.side = side
        self.time = time.strftime("%d-%m-%Y %H:%M:%S")


class Position:
    def __init__(self, time_opened: datetime, volume: float, size: float, price: float,
                 position_container: 'PositionContainer', id: int):
        self.opened_time = time_opened
        self.position_container = position_container
        self.id = id
        self.volume = volume
        self.initial_size = size
        self.enter_price = price
        self.closed_amount = 0
        self.total_return = None
        self.winning = None
        self.total_return_percent = None
        self.closed_time = None
        self.avg_close_price = None
        self.is_active = True
        self.time_in_trade = None
        self.time_series = {
            'value': [],
            'return': [],
            'return_percent': [],
            'times': [],
            'volume': [],
            'closed_amount': []
        }

        self.transactions = [Transaction(volume=volume, price=price, side=OrderSide.BUY, time=time_opened)]
        self.shares = SharesCounter()
        self.shares.add_share_count(ShareCount(num_shares=volume, price=price))

    def sell_off(self, order_volume: float, order_price: float, time: datetime) -> Tuple[bool, float, Union[int, float]]:

        """
        Method to partially close a position. Incrementing the partial return member variable by the order size.
        Decrements the self.remaining_volume member variable by the volume of the partial close
        If self.remaining_volume is then totalled to 0, calculate the average close price which triggers the
        final closure of the position. Average close price is calculated by volume weighting

        :param order_volume: volume of the partial close
        :param order_price: Price at which the position was partially closed
        :param time: Datetime object
        :return: Tuple of is_closed flag indicating whether or not a position is fully closed out or not and remaining
        order volume.
        """

        filled_order_volume = min(order_volume, self.volume)
        size = filled_order_volume * order_price
        remaining_order_volume = order_volume - filled_order_volume
        self.transactions.append(Transaction(volume=filled_order_volume,
                                             price=order_price,
                                             time=time,
                                             side=OrderSide.SELL))

        _ = self.shares.sell_off(num_shares=order_volume)

        #if self.volume == 0:
        if self.volume - filled_order_volume == 0:
            self.close_out(time=time)

        self.volume -= filled_order_volume
        self.closed_amount += size

        return self.is_active, filled_order_volume, remaining_order_volume

    def increase(self, order_volume: float, order_price: float, time: datetime) -> None:
        self.volume += order_volume
        self.shares.add_share_count(share_count=ShareCount(num_shares=order_volume, price=order_price))

        transaction = Transaction(volume=order_volume, price=order_price, side=OrderSide.BUY, time=time)
        self.transactions.append(transaction)

    def close_out(self, time: datetime):
        """ Function to close out position. First updates time series
         and then calculate metrics on exit."""
        self.update()

        self.closed_time = time
        self.avg_close_price = sum([t.volume * t.price for t in self.transactions]) / sum(
            [t.volume for t in self.transactions])

        self.total_return = self.current_return
        self.total_return_percent = self.current_return_percent
        self.is_active = False
        self.winning = True if self.total_return > 0 else False

    @property
    def total_buy_size(self) -> float:
        return sum([t.size for t in self.transactions if t.side == OrderSide.BUY])

    @property
    def total_sell_size(self) -> float:
        return sum([t.size for t in self.transactions if t.side == OrderSide.SELL])

    @property
    def value(self) -> float:
        return self.volume * self.position_container.asset.bars[0].close

    @property
    def current_return(self) -> float:
        return self.value + self.closed_amount - self.total_buy_size

    @property
    def current_return_percent(self) -> float:
        return self.current_return / self.total_buy_size

    def update(self):

        """
        Method to update the position metrics each time a new time series data event is received received
        by the event handler
        """

        current_time = self.position_container.context.time

        self.time_series['value'].append(self.value)
        self.time_series['volume'].append(self.volume)
        self.time_series['return'].append(self.current_return)
        self.time_series['return_percent'].append(self.current_return_percent)
        self.time_series['closed_amount'].append(self.closed_amount)
        self.time_series['times'].append(current_time.strftime("%d-%m-%Y %H:%M:%S"))
        self.time_in_trade = (current_time - self.opened_time)

    def __repr__(self):
        return 'id: {} - volume: {}'.format(self.id, self.volume)

    def report(self):
        try:
            closed_time = self.closed_time.strftime("%d-%m-%Y %H:%M:%S")
        except AttributeError:
            closed_time = None

        # TODO Find a way to get the base asset in here as well
        data = {
            'id': self.id,
            'opened_time': self.opened_time.strftime("%d-%m-%Y %H:%M:%S"),
            'closed_time': closed_time,
            'enter_price': self.enter_price,
            'avg_close_price': self.avg_close_price,
            'total_return': self.total_return,
            'total_buy_size': self.total_buy_size,
            'total_sell_size': self.total_sell_size,
            'total_return_percent': self.total_return_percent,
            'values': self.time_series['value'],
            'returns': self.time_series['return'],
            'maximum_drawdown': drawdown(self.time_series['value']),
            'return_percent': self.time_series['return_percent'],
            'days_in_trade': self.time_in_trade.days,
            'hours_in_trade': self.time_in_trade.total_seconds()/(60*60),
            'minutes_in_trade': self.time_in_trade.total_seconds()/60,
            'times': self.time_series['times'],
            'volumes': self.time_series['volume'],
            'transactions': [t.__dict__ for t in self.transactions],
            'num_transactions': {
                OrderSide.BUY.value: sum([1 for t in self.transactions if t.side == OrderSide.BUY]),
                OrderSide.SELL.value: sum([1 for t in self.transactions if t.side == OrderSide.SELL]),
            }

        }

        try:
            data['closed'] = self.closed_time.strftime("%d-%m-%Y %H:%M:%S")
        except AttributeError:
            data['closed'] = "Position not closed"

        return data


class PositionContainer:

    """
    A position container holding positions for an asset in the account
    """

    def __init__(self, asset: Asset, context: Context):
        self.position: Union[Position, None] = None
        self.exited_positions: List[Position] = list()
        self.context = context
        self.asset = asset
        self.latest_active_id = 0

    @property
    def winning_positions(self) -> List[Position]:
        """ Returns the list of all exited positions with winning = True"""
        return [p for p in self.exited_positions if p.winning]

    @property
    def losing_positions(self) -> List[Position]:
        """ Returns the list of all exited positions with winning = False """
        return [p for p in self.exited_positions if not p.winning]

    @property
    def num_winning_positions(self) -> int:
        """ Returns the number of positions with winning = True"""
        return len(self.winning_positions)

    @property
    def num_losing_positions(self) -> int:
        """ Returns the number of positions with winning = False """
        return len(self.losing_positions)

    @property
    def tot_win_pos_return(self) -> float:
        """ Returns the total winning position returns """
        return sum([p.total_return for p in self.winning_positions])

    @property
    def tot_win_pos_return_percent(self) -> float:
        """ Returns the sum of all the winning position percentage returns """
        return sum([p.total_return_percent for p in self.winning_positions])

    @property
    def tot_los_pos_return_percent(self) -> float:
        """ Returns the sum of all the losing position percentage returns """
        return sum([p.total_return_percent for p in self.losing_positions])

    @property
    def tot_los_pos_return(self) -> float:
        """ Returns the total losing position returns"""
        return sum([p.total_return for p in self.losing_positions])

    def enter_position(self, time: datetime, volume: Union[int, float], size: float, price: float) -> None:
        """
        Enters a position. If an open position exists on the asset, increase the position with the new order.
        If no open position exists on the asset, open a new one.
        """
        if self.position is not None:
            self.position.increase(order_volume=volume, order_price=price, time=time)
        else:
            position = Position(time_opened=time,
                                volume=volume,
                                size=size,
                                price=price,
                                position_container=self,
                                id=self.latest_active_id)
            self.latest_active_id += 1
            self.position = position

    def sell_off(self, volume: Union[int, float], price: float, time: datetime) -> None:

        """
        Method that sells of "size" amount of the oldest position of asset "ticker" at the price "price" at the
        timestamp "timestamp"

        :param volume: The order volume
        :param price: The order price
        :param time: The timestamp
        """

        remaining_volume = volume
        is_active, filled_volume, remaining_volume = self.position.sell_off(order_volume=remaining_volume,
                                                                            order_price=price,
                                                                            time=time)
        if not is_active:
            self.exited_positions.append(self.position)
            self.position = None

    def update_position(self):
        if self.position is not None:
            self.position.update()

    def report(self):
        data = {}
        if self.position is not None:
            data[self.position.id] = self.position.report()
        for p in self.iter_exited():
            data[p.id] = p.report()
        return data

    def iter_active(self):
        for ticker in self.active_positions.keys():
            for p in self.active_positions[ticker]:
                yield p

    def iter_exited(self):
        for p in self.exited_positions:
            yield p
