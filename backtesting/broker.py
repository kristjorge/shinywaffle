import numpy.random as rand
from common.event import events
from utils.misc import round_down
from common.context import Context
from backtesting import order


class BacktestBroker:

    """
    Base class for broker objects.
    Will contain logic for getting order prices

    Modelling slippage as a normal distribution with mean 0 and standard deviation of 0.05

    """

    slippages = abs(rand.normal(0, 0.05, 100000)).tolist()

    def __init__(self, context: Context, fee: float, min_order_size: float = None, min_order_currency: str = 'USD'):
        self.context = context
        self.name = 'Basic broker'
        self.fee = fee
        self.min_order_size = min_order_size
        self.min_order_currency = min_order_currency
        self.total_commission = 0
        self.order_book = order.OrderBook(context)
        context.broker = self

    def place_order(self, new_order):
        pending_order_event = None
        self.order_book.new_order(new_order)
        if new_order.type == 'market':
            pending_order_event = events.PendingMarketOrderEvent(new_order.asset,
                                                                 new_order.order_volume,
                                                                 new_order.side,
                                                                 new_order.time_placed)
        elif new_order.type == 'limit':
            pending_order_event = events.PendingLimitOrderEvent(new_order.asset,
                                                                new_order.order_limit_price,
                                                                new_order.order_volume,
                                                                new_order.side,
                                                                new_order.time_placed)
        return pending_order_event

    def buy_order_fill_confirmation(self, event):
        if type(event) == events.MarketBuyOrderPlacedEvent:
            order_price = self.request_market_order_price(event)
            order_type = 'market'
        elif type(event) == events.LimitBuyOrderPlacedEvent:
            order_price = event.order_limit_price
            order_type = 'limit'
        else:
            order_price = None
            order_type = None

        order_size = event.order_volume * order_price
        commission = self.calculate_commission(order_size)

        return events.OrderFilledEvent(event.asset,
                                       order_price,
                                       order_size,
                                       event.order_volume,
                                       order_type,
                                       'buy',
                                       commission,
                                       self.context.retrieved_data.time)

    def sell_order_fill_confirmation(self, event):
        if type(event) == events.MarketSellOrderPlacedEvent:
            order_price = self.request_market_order_price(event)
            order_type = 'market'
        elif type(event) == events.LimitSellOrderPlacedEvent:
            order_price = event.order_limit_price
            order_type = 'limit'
        else:
            order_price = None
            order_type = None

        order_size = event.order_volume * order_price
        commission = self.calculate_commission(order_size)
        return events.OrderFilledEvent(event.asset,
                                       order_price,
                                       order_size,
                                       event.order_volume,
                                       order_type,
                                       'sell',
                                       commission,
                                       self.context.retrieved_data.time)

    def request_market_order_price(self, event) -> float:
        time_series_data = self.context.retrieved_data[event.asset.ticker]
        slippage = BacktestBroker.slippages.pop()
        if type(event) == events.MarketSellOrderPlacedEvent:
            pass
        elif type(event) == events.MarketBuyOrderPlacedEvent:
            slippage *= -1
        return time_series_data['bars'][0].close + slippage

    def calculate_commission(self, order_size: float) -> float:
        """
        This is a simple commission calculation taking the order size and multiply it by the fee percentage
        :param order_size:
        :return:
        """
        commission = order_size * self.fee
        self.total_commission += commission
        return commission

    def self2dict(self):
        data = {
            'name': self.name,
            'fee': self.fee,
            'min order size': self.min_order_size,
            'min order size currency': self.min_order_currency,
            'total commission': self.total_commission
        }

        return data


class InteractiveBrokers(BacktestBroker):

    """
    InteractiveBrokers broker class

    """
    def __init__(self, context: Context):
        super().__init__(context, 0.0005, 5, 'USD')
        self.name = 'Interactive Brokers'

    def calculate_commission(self, order_size: float) -> float:
        commission = order_size * self.fee
        self.total_commission += commission
        return commission


class Binance(BacktestBroker):
    """
    Binance cryptocurrency exchange / broker class

    """

    def __init__(self, context: Context):
        super().__init__(context, 0.001, 0, 'BTC')
        self.name = 'Binance'

    def calculate_commission(self, order_size):
        commission = order_size * self.fee
        self.total_commission += commission
        return commission
