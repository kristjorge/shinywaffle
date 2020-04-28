from common.context import Context


class PositionContainer:

    """
    Positions are closed FIFO
    """

    # TODO: Consider stop using class variables for incrementing ID. Can cause problems in multithreading during workflow
    latest_active_id = 0

    def __init__(self, context: Context):
        self.active_positions = {asset: [] for asset in context.assets.keys()}
        self.exited_positions = {asset: [] for asset in context.assets.keys()}
        self.account = context.account
        self.context = context
        PositionContainer.latest_active_id = 0

    def enter_position(self, p):
        self.active_positions[p.asset.ticker].append(p)
        self.active_positions[p.asset.ticker][-1].id = PositionContainer.latest_active_id
        PositionContainer.latest_active_id += 1

    def sell_off_position(self, ticker, volume, price, timestamp):
        """

        Method that sells of "size" amount of the oldest position of asset "ticker" at the price "price" at the
        timestamp "timestamp"

        :param ticker: Ticker of the asset that is being sold
        :param volume: The order volume
        :param price: The order price
        :param timestamp: The timetamp
        """

        is_active = self.active_positions[ticker][0].sell_off(volume, price, timestamp)
        if not is_active:
            self.exited_positions[ticker].append(self.active_positions[ticker].pop(0))

    def update_positions(self):
        for p in self.iter_active():
            p.update(self.context.retrieved_data)

    def report(self):
        data = {}
        for p in self.iter_active():
            data[p.id] = p.self2dict()
        for p in self.iter_exited():
            data[p.id] = p.self2dict()
        return data

    def iter_active(self):
        for ticker in self.active_positions.keys():
            for p in self.active_positions[ticker]:
                yield p

    def iter_exited(self):
        for ticker in self.exited_positions.keys():
            for p in self.exited_positions[ticker]:
                yield p
