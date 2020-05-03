import numpy.random as rand
from common.event import events
from common.context import Context
from backtesting import orders as orders_module


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
        self.order_book = orders_module.OrderBook(context)
        context.broker = self

    def place_order(self, new_order):
        pending_order_event = self.order_book.new_order(new_order)
        return pending_order_event

    def check_for_order_fill(self, order_id):
        order = self.order_book.get_by_id(order_id)
        event = None
        if isinstance(order, orders_module.MarketOrder):
            event = self.fill_market_order(order)

        elif isinstance(order, orders_module.LimitOrder):
            print('Checking for limit order filling')

        return event

    def fill_market_order(self, order):
        price = self.get_market_order_price(order)
        order_size = order.volume * price
        commission = self.calculate_commission(order_size)
        order_filled_event = self.order_book.fill_order(order.id, price, order_size, commission)
        return order_filled_event

    def get_market_order_price(self, order) -> float:
        price_data = self.context.retrieved_data[order.asset.ticker]
        slippage = BacktestBroker.slippages.pop()
        if isinstance(order, orders_module.BuyOrder):
            pass
        if isinstance(order, orders_module.SellOrder):
            slippage *= -1
        return price_data['bars'][0].close + slippage

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
