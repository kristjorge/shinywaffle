from shinywaffle.common.context import Context
from shinywaffle.utils.misc import round_down
from abc import ABC, abstractmethod
from typing import Union


class RiskManager(ABC):

    def __init__(self, context: Context):
        context.risk_manager = self
        self.context = context
        try:
            self.account = context.account
        except AttributeError:
            pass

        try:
            context.account.risk_manager = self
        except AttributeError:
            pass

    @abstractmethod
    def calculate_position_volume(self, ticker: str) -> Union[int, float]:
        """
        Method to calculate position size. Returns the number of stocks (int) or the number forex / crypto
        as a float
        :return: 
        """
        pass


class BaseRiskManager(RiskManager):

    def __init__(self, context):
        super().__init__(context)

    def calculate_position_volume(self, ticker: str) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position volume
        """
        asset = self.context.assets[ticker]
        last_observed_close = asset.bars[0].close
        position_size = self.account.base_balance.balance * 0.10
        volume = round_down(position_size / last_observed_close, asset.num_decimal_points)
        return volume
