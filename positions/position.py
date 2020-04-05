from collections import namedtuple


class Position:

    transaction = namedtuple("Transaction", ["volume", "price", "size", "transaction time"])

    def __init__(self, timestamp_generated, timestamp_confirmed, asset, action_type, volume, size, price):
        self.generated = timestamp_generated
        self.confirmed = timestamp_confirmed
        self.asset = asset
        self.type = action_type
        self.volume = volume
        self.volume_remaining = volume
        self.size = size
        self.enter_price = price
        self.partial_return = 0
        self.closed = None
        self.close_price = None
        self.active = True

        self.time_series = {
            'value': [],
            'return': [],
            'return percentage': [],
            'time in trade': [],
            'times': [],
            'volume remaining': []
        }

        self.transactions = []

    def close(self, price, timestamp_closed):
        """
        Method is called to close out an active position.
        :param price: The close price for the asset
        :param timestamp_closed: The timestamp that the position was closed out. type: datetime
        :return:
        """
        self.closed = timestamp_closed
        self.close_price = price
        self.active = False
        self.transactions.append(Position.transaction(self.volume, price, self.volume * price, timestamp_closed))

    def partial_close(self, size, price, timestamp):
        """

        Method to partially close a position. Incrementing the partial return member variable by the order size.
        Decrements the self.remaining_volume member variable by the volume of the partial close

        :param size: Size of the partial close
        :param price: Price at which the position was partially closed
        :param timestamp: Datetime object
        :return:
        """
        volume = size / price
        self.partial_return += size
        self.volume_remaining -= volume
        self.transactions.append(Position.transaction(volume, price, size, timestamp))

    def calculate_closing_metrics(self):
        pass

    def update(self, bar, current_time):
        self.time_series['value'].append(self.volume * bar['close'])
        self.time_series['return'].append(self.volume * bar['close'] - self.volume * self.enter_price)
        self.time_series['return percentage'].append(self.time_series['return'][-1] / self.size)
        self.time_series['time'].append(current_time)
        self.time_series['time in trade'].append((current_time - self.confirmed).days)
        try:
            self.time_series['volume remaining'].append(self.time_series['volume remaining'][-1])
        except IndexError:
            self.time_series['volume remaining'].append(self.volume_remaining)
