from __future__ import annotations
import numpy as np
from shinywaffle.common.context import Context
from shinywaffle.backtesting import orders as orders_module
from shinywaffle.data.intrabar_simulation import simulate_intrabar_data
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from shinywaffle.common.event.events import OrderFilledEvent
    from shinywaffle.backtesting.orders import ANY_ORDER_TYPE


class BacktestBroker:

    """
    Base class for broker objects.
    Will contain logic for getting order prices



    """

    def __init__(self, context: Context, fee: float, slippage=True):
        """
        Modelling slippage as a normal distribution with mean 0 and standard deviation of 0.05. Generating 100000
        values.

        :param context: Context object containing all the cogs
        :param fee: Fee percentage
        """
        n = 100000
        self.context = context
        self.name = 'Backtest broker'
        self.fee = fee
        self.total_commission = 0
        self.total_slippage = 0
        self.order_book = orders_module.OrderBook(context)
        if slippage is not True:
            self.slippages = [0] * n
        else:
            self.slippages = abs(np.random.normal(0, 0.05, n)).tolist()

    def place_order(self, new_order: ANY_ORDER_TYPE):

        """
        :param new_order: The order object received by the broker. Submitted further on to the order_book object
        and receives a PendingOrderEvent.
        :return: PendingOrderEvent
        """

        pending_order_event = self.order_book.new_order(order=new_order)
        return pending_order_event

    def check_for_order_fill(self, order_id: int) -> Union[None, OrderFilledEvent]:

        """
        Method that checks whether or not an order with a given ID will be filled in the current bar.

        The order object is fetched from the order_book by its ID. If it is a market order, then it is automatically
        filled and the price is calculated from the self.get_market_order_price method. If the order is a limit order,
        then the order limit price is checked against the prices in the current bar to see if the limit price is reached within the bar.

        If so, then the intrabar prices are simulated using the simulate_intrabar_data method. 
            If the order is a buy order, the order will be filled at the price that is first equal to or below the order limit price. 
            If it is a sell order, then it will be filled at the price that is first equal to or above the order limit price.

        :param order_id: ID of the order to check
        :return: OrderFilledEvent
        """

        order = self.order_book.get_by_id(order_id)
        event = None

        # If MarketOrder then fill immediately with the price from the get_market_order_price
        if isinstance(order, orders_module.MarketBuyOrder) or isinstance(order, orders_module.MarketSellOrder):
            price = self.get_market_order_price(order=order)
            slippage = self.get_market_order_slippage(order=order)

            # The final order price is the open price of the bar + the slippage in %
            # For buy order, slippage is positive
            # For sell order, slippage is negative
            slipped_price = price * slippage
            new_price = price + slipped_price
            self.total_slippage += abs(slipped_price * order.volume)
            event = self.fill_order(order=order, fill_price=new_price, order_price=price)

        # If LimitOrder, then check whether or not the limit is reached, and if so simulate the price action.
        elif isinstance(order, orders_module.LimitBuyOrder) or isinstance(order, orders_module.LimitSellOrder):
            if self.is_order_within_bar(order):
                bars = order.asset.bars
                bar = bars[0]

                # total_t = (bar.time - previous_bar.time).days
                # Total_t = 1 means that bar duration is normalized
                # and the price simulation will then generate 1 / dt price points per bar.

                total_t = 1.
                intra_bar_prices = simulate_intrabar_data(bar, total_t, 0.01)

                # Finding fill price for BuyOrder
                if type(order) == orders_module.LimitBuyOrder:
                    for price in intra_bar_prices:
                        if price <= order.order_limit_price:
                            event = self.fill_order(order=order, fill_price=price, order_price=price)
                            break

                # Finding fill price for SellOrder
                elif type(order) == orders_module.LimitSellOrder:
                    for price in intra_bar_prices:
                        if price >= order.order_limit_price:
                            event = self.fill_order(order=order, fill_price=price, order_price=price)
                            break

        return event

    @staticmethod
    def is_order_within_bar(order: Union[orders_module.LimitBuyOrder, orders_module.LimitSellOrder]) -> bool:

        """
        Method that checks whether or not the limit order price is within the latest retrieved bar for a given asset.
        Returns True if it is and False if not.

        :param order: Order object containing the order limit price
        :return: True/False
        """

        bar = order.asset.bars[0]
        return bar.low <= order.order_limit_price <= bar.high

    def fill_order(self, order: ANY_ORDER_TYPE, fill_price: float, order_price: float) -> OrderFilledEvent:

        """
        Method that fills an order at a given price.
            The order size is calculate: order.volume * price
            Commission is calculated from the calculate_commission() method from the order size

        The order_book.fill_order is called with the order.ID, size and commission and returns a OrderFilledEvent
        :param order: The order object that was filled
        :param fill_price: The price the order was filled at
        :param order_price: The price that the order was sent to the market at
        """

        order_size = order.volume * fill_price
        commission = self.calculate_commission(order_size=order_size)
        order_filled_event = self.order_book.fill_order(pending_order_id=order.id,
                                                        filled_price=fill_price,
                                                        order_price=order_price,
                                                        size=order_size,
                                                        commission=commission)
        return order_filled_event

    def get_market_order_slippage(self, order: Union[orders_module.MarketBuyOrder, orders_module.MarketSellOrder]) -> float:
        """
        Returns a slippage factor from the slippage factors that have been saved

        If the order is a buy order, the slippage is positive to make the order price larger than the bar price
        If the order is a sell order, the slippage is negative to make the order price smaller than the bar price
        """

        slippage = self.slippages.pop(0)
        if isinstance(order, orders_module.SellOrder):
            slippage *= -1

        return slippage

    def get_market_order_price(self, order: Union[orders_module.MarketBuyOrder, orders_module.MarketSellOrder]) -> float:

        """
        Method to get the fill price for a market order. Assuming the market order is filled at the open of the
        current bar. This would be valid since it is filled in the bar after it was submitted

        Returns: the market order price (float) for the order
        """

        return order.asset.bars[0].open

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
            'total_commission': self.total_commission,
            'total_slippage': self.total_slippage,
            'order_book': self.order_book.report()
        }

        return data

