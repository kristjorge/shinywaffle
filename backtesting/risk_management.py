from backtesting.account import Account


class RiskManager:

    def __init__(self, account: Account):
        self.account = account

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size
        :return: 
        """
        raise NotImplementedError


class BaseRiskManager(RiskManager):

    def __init__(self, account: Account):
        super().__init__(account)

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position size in relevant currency
        """
        position_size = self.account.cash * 0.05
        return position_size
