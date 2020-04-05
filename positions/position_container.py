from positions import position


class PositionContainer:

    def __init__(self, assets):
        self.active_positions = {asset.ticker: [] for asset in assets.values()}
        self.exited_positions = {asset.ticker: [] for asset in assets.values()}

    def enter_position(self, p):
        self.active_positions[p.asset.ticker] = p
