from backtesting.portfolio import Portfolio

class RiskManager:

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size
        :return: 
        """
        raise NotImplementedError


class BaseRiskManager(RiskManager):

    def __init__(self, portfolio):
        super().__init__(portfolio)

    def calculate_position_size(self) -> float:
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position size in relevant currency
        """
        position_size = self.portfolio.cash * 0.05
        return position_size
