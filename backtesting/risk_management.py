

class RiskManager:

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def calculate_position_size(self):
        """
        Method to calculate position size based on historical data.
        For now only returns 5 % of available cash
        :return: desired position size in relevant currency
        """
        position_size = self.portfolio.cash * 0.05
        return position_size
