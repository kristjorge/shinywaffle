from common.context import Context


class RiskManager:

    def __init__(self):
        Context.risk_manager = self
        try:
            self.account = Context.account
        except AttributeError:
            print('Account not provided in context... ')

        try:
            Context.account.risk_manager = self
        except AttributeError:
            print('Account not provided in context...')

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size
        :return: 
        """
        raise NotImplementedError


class BaseRiskManager(RiskManager):

    def __init__(self,):
        super().__init__()

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position size in relevant currency
        """
        position_size = self.account.cash * 0.05
        return position_size
