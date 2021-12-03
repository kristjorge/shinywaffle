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

    @abstractmethod
    def position_size_entry(self, asset: Asset) -> Union[int, float]:
        """
        Method to calculate position size when entering a position.
        Returns the number of stocks (int) or the number forex / crypto
        as a float

        :return Union[int, float]: The position size to enter or exit
        """
        pass

    @abstractmethod
    def position_size_exit(self, asset: Asset) -> Union[int, float]:
        """
        Method to calculate position size when exiting a position.
        Returns the number of stocks (int) or the number forex / crypto
        as a float

        :return Union[int, float]: The position size to enter or exit
        """
        pass


class BaseRiskManager(RiskManager):

    def __init__(self, context):
        super().__init__(context)

    def position_size_entry(self, asset: Asset) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 10 % of available cash
        :return: desired position volume
        """
        last_observed_close = asset.bars[0].close
        position_size = self.context.account.base_balance.balance * 0.10
        volume = round_down(position_size / last_observed_close, asset.num_decimal_points)
        return volume

    def position_size_exit(self, asset: Asset) -> Union[int, float]:
        """ Exiting the entire position"""
        available_volume = self.context.account.balances[asset].balance
        return available_volume
