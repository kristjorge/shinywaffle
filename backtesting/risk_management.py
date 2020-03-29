

class RiskManager:

    def __init__(self):
        self.position_sizes = []

    def calculate_position_size(self):
        """
        Method to calculate position size based on historical data.
        For now only returns 100 USD
        :return: desired position size in relevant currency
        """
        position_size = 100
        self.position_sizes.append(position_size)
        return position_size
