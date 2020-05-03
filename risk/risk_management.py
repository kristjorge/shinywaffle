from common.context import Context
from utils.misc import round_down


class RiskManager:

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

    def calculate_position_volume(self, ticker) -> float:
        """
        Method to calculate position size
        :return: 
        """
        raise NotImplementedError


class BaseRiskManager(RiskManager):

    def __init__(self, context):
        super().__init__(context)

    def calculate_position_volume(self, ticker) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position volume
        """
        asset = self.context.assets[ticker]
        last_observed_close = self.context.retrieved_data[ticker]['bars'][0].close
        position_size = self.account.cash * 0.10
        volume = round_down(position_size / last_observed_close, asset.num_decimal_points)
        return volume
