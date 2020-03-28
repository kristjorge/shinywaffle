"""

Class holding the initial holding in a base currency for the backtesting

"""


class Portfolio:

    available_currencies = ("USD", "NOK", "GBP", "EUR")

    def __init__(self, initial_holding, currency, assets):
        assert isinstance(assets, list)
        assert currency in Portfolio.available_currencies

        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_currency = currency
        self.assets = {asset.ticker: {'holding': [0.], 'value': [0.], 'asset_data': asset} for asset in assets}

    def debit(self, amount):
        self.cash += amount

    def credit(self, amount):
        self.cash -= amount

    def update_asset_values(self):
        total_value = self.cash
        for asset in self.assets.values():
            try:
                asset['value'] = asset['holding'] * asset['asset_data'].latest_bar.close
            except TypeError:
                asset['value'] = 0
            total_value += asset['value']

        self.total_value = total_value

