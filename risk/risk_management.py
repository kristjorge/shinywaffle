from common.context import Context


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

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size
        :return: 
        """
        raise NotImplementedError


class BaseRiskManager(RiskManager):

    def __init__(self,context):
        super().__init__(context)

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position size in relevant currency
        """
        position_size = self.account.cash * 0.05
        return position_size
