import numpy as np
from common.context import Context
from backtesting import orders as orders_module
from data.intrabar_simulation import simulate_intrabar_data
from datetime import timedelta


class BacktestBroker:

    """
    Base class for broker objects.
    Will contain logic for getting order prices

    Modelling slippage as a normal distribution with mean 0 and standard deviation of 0.05

    """

    def __init__(self, context: Context, fee: float):
        self.context = context
        self.name = 'Basic broker'
        self.fee = fee
        self.total_commission = 0
        self.order_book = orders_module.OrderBook(context)
        self.slippages = abs(np.random.normal(0, 0.05, 100000)).tolist()
        context.broker = self

    def place_order(self, new_order):
        pending_order_event = self.order_book.new_order(new_order)
        return pending_order_event

    def check_for_order_fill(self, order_id):
        order = self.order_book.get_by_id(order_id)
        event = None
        if isinstance(order, orders_module.MarketOrder):
            price = self.get_market_order_price(order)
            event = self.fill_order(order, price)

        elif isinstance(order, orders_module.LimitOrder):
            event = None
            if self.is_order_within_bar(order):
                bar = self.context.retrieved_data[order.asset.ticker]['bars'][0]
                previous_bar = self.context.retrieved_data[order.asset.ticker]['bars'][1]
                total_t = (bar.time - previous_bar.time).days
                intra_bar_prices = simulate_intrabar_data(bar, total_t, 0.01)

                # Finding fill price for BuyOrder
                if isinstance(order, orders_module.BuyOrder):
                    for price in intra_bar_prices:
                        if price <= order.order_limit_price:
                            # event = self.fill_order(order, order.order_limit_price)
                            event = self.fill_order(order, price)
                            break

                # Finding fill price for SellOrder
                elif isinstance(order, orders_module.SellOrder):
                    for price in intra_bar_prices:
                        if price >= order.order_limit_price:
                            # event = self.fill_order(order, order.order_limit_price)
                            event = self.fill_order(order, price)
                            break

        return event

    def is_order_within_bar(self, order) -> bool:
        bar = self.context.retrieved_data[order.asset.ticker]['bars'][0]
        if bar.low <= order.order_limit_price <= bar.high:
            return True
        else:
            return False

    def fill_order(self, order, price):

        order_size = order.volume * price
        commission = self.calculate_commission(order_size)
        order_filled_event = self.order_book.fill_order(order.id, price, order_size, commission)
        return order_filled_event

    def get_market_order_price(self, order) -> float:
        price_data = self.context.retrieved_data[order.asset.ticker]
        slippage = self.slippages.pop()
        if isinstance(order, orders_module.BuyOrder):
            pass
        if isinstance(order, orders_module.SellOrder):
            slippage *= -1

        # Open or close price? Should be open price if it is filled during the next bar
        return price_data['bars'][0].open + slippage

    def calculate_commission(self, order_size: float) -> float:
        """
        This is a simple commission calculation taking the order size and multiply it by the fee percentage
        :param order_size:
        :return:
        """
        commission = order_size * self.fee
        self.total_commission += commission
        return commission

    def report(self):
        data = {
            'name': self.name,
            'fee': self.fee,
            'total commission': self.total_commission
        }

        return data

