import numpy as np
from common.context import Context
from backtesting import orders as orders_module
from data.intrabar_simulation import simulate_intrabar_data
from datetime import timedelta


class BacktestBroker:

    """
    Base class for broker objects.
    Will contain logic for getting order prices



    """

    def __init__(self, context: Context, fee: float):
        """
        Modelling slippage as a normal distribution with mean 0 and standard deviation of 0.05. Generating 100000
        values.

        :param context: Context object containing all the cogs
        :param fee: Fee percentage
        """
        self.context = context
        self.name = 'Basic broker'
        self.fee = fee
        self.total_commission = 0
        self.order_book = orders_module.OrderBook(context)
        self.slippages = abs(np.random.normal(0, 0.05, 100000)).tolist()
        context.broker = self

    def place_order(self, new_order):

        """
        :param new_order: The order object received by the broker. Submitted further on to the order_book object
        and recieves a PendingOrderEvent.
        :return: PendingOrderEvent
        """

        pending_order_event = self.order_book.new_order(new_order)
        return pending_order_event

    def check_for_order_fill(self, order_id):

        """
        Method that checks whether or not an order with a given ID will be filled in the current bar.

        The order object is gotten from the order_book by its ID. If it is a market order, then it is automatically
        filled and the price is calculated from the self.get_market_order_price method. If the order is a limit order,
        then the order limit price is checked versus the current bar to see if it would be possible to fill.

        If is will be filled, then the intra bar prices are simulated using the simulate_intrabar_data method. If the
        order is a buy order, the order will be filled at the price that is first equal to or below the order limit
        price. If it is a sell order, then it will be filled at the price that is first equal to or above the
        order limit price.

        :param order_id: ID of the order to check
        :return: OrderFilledEvent
        """

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

        """
        Method that checks whether or not the limit order price is within the latest retrieved bar for a given asset.
        Returns True if it is and False if not.

        :param order: Order object containing the order limit price
        :return: True/False
        """

        bar = self.context.retrieved_data[order.asset.ticker]['bars'][0]
        if bar.low <= order.order_limit_price <= bar.high:
            return True
        else:
            return False

    def fill_order(self, order, price):

        """
        Method that fills an order at a given price.
            The order size is calculate: order.volume * price
            Commission is calculated from the calculate_commission() method from the order size

        The order_book.fill_order is called with the order.ID, size and commission and returns a OrderFilledEvent
        :param order: Order to fill
        :param price: Fill price of the order
        :return: OrderFilledEvent
        """

        order_size = order.volume * price
        commission = self.calculate_commission(order_size)
        order_filled_event = self.order_book.fill_order(order.id, price, order_size, commission)
        return order_filled_event

    def get_market_order_price(self, order) -> float:

        """
        Method to get the fill price for a market order. Assuming the market order is filled at the open of the
        current bar. This would be valid since it is filled in the bar after it was submitted

        Slippage is taken from the self.slippages list. If the order is a sell order, the slippage is subtracted, and
        if it is a buy order it is added to the price to produce the final fill price.

        :param order:
        :return:
        """

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

