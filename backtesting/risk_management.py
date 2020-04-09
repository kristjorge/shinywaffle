

class RiskManager:

    def __init__(self, portfolio):
        self.portfolio = portfolio

    @staticmethod
    def calculate_position_size():
        """
        Method to calculate position size based on historical data.
        For now only returns 100 USD
        :return: desired position size in relevant currency
        """
        position_size = 100
        return position_size
