from collections import namedtuple
from datetime import datetime


class Position:

    Transaction = namedtuple("Transaction", ["volume", "price", "size", "time"])

    def __init__(self, time_opened: datetime, asset, volume: float, size: float, price: float):
        self.opened = time_opened
        self.asset = asset
        self.id = None
        self.volume = volume
        self.volume_remaining = volume
        self.size = size
        self.enter_price = price
        self.partial_closed_amount = 0
        self.closed = None
        self.close_price = None
        self.is_active = True
        self.time_in_trade = 0
        self.time_series = {
            'value': [],
            'return': [],
            'return percentage': [],
            'times': [],
            'volume remaining': []
        }
        self.transactions = []

    def sell_off(self, order_volume: float, order_price: float, time: datetime):
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

        filled_order_volume = min(order_volume, self.volume_remaining)
        size = filled_order_volume * order_price
        self.partial_closed_amount += size
        self.volume_remaining -= filled_order_volume
        remaining_order_volume = order_volume - filled_order_volume
        self.transactions.append(Position.Transaction(filled_order_volume, order_price, size, time))

        if self.volume_remaining == 0:
            self.closed = time
            self.close_price = sum([t.volume * t.price for t in self.transactions]) / sum([t.volume for t in self.transactions])
            self.is_active = False

        return self.is_active, filled_order_volume, remaining_order_volume

    def update(self, retrieved_data):

        """
        Method to update the position metrics each time a new time series data event is received received
        by the event handler
        :param retrieved_data: Time series data object received by the data provider
        """

        close_price = retrieved_data[self.asset.ticker]['bars'][0].close
        current_time = retrieved_data.time
        remaining_value = self.volume_remaining * close_price

        self.time_series['value'].append(remaining_value + self.partial_closed_amount)
        self.time_series['return'].append(remaining_value + self.partial_closed_amount - self.volume * self.enter_price)
        self.time_series['return percentage'].append(self.time_series['return'][-1] / self.size)
        self.time_series['times'].append(current_time.strftime("%d-%m-%Y %H:%M:%S"))
        self.time_in_trade = (current_time - self.opened).days
        try:
            self.time_series['volume remaining'].append(self.time_series['volume remaining'][-1])
        except IndexError:
            self.time_series['volume remaining'].append(self.volume_remaining)

    def __repr__(self):
        return 'id: {} - volume remaining: {}'.format(self.id, self.volume_remaining)

    def report(self):
        try:
            closed_time = self.closed.strftime("%d-%m-%Y %H:%M:%S")
        except AttributeError:
            closed_time = 'still open'

        data = {
            'id': self.id,
            'asset': self.asset.name,
            'opened': self.opened.strftime("%d-%m-%Y %H:%M:%S"),
            'closed': closed_time,
            'volume': self.volume,
            'size': self.size,
            'enter price': self.enter_price,
            'volume weighted close price': self.close_price,

            'time series': {
                'value': self.time_series['value'],
                'return': self.time_series['return'],
                'return percentage': self.time_series['return percentage'],
                'time in trade': self.time_in_trade,
                'times': self.time_series['times'],
                'volume remaining': self.time_series['volume remaining']
            }
        }

        try:
            data['closed'] = self.closed.strftime("%d-%m-%Y %H:%M:%S")
        except AttributeError:
            data['closed'] = "Position not closed"

        return data
