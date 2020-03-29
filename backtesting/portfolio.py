from backtesting import risk_management

"""

Class holding the initial holding in a base currency for the backtesting

"""


class Portfolio:

    available_currencies = ("USD", "NOK", "GBP", "EUR")

    def __init__(self, initial_holding, currency, assets, risk_manager):
        assert isinstance(assets, list)
        assert isinstance(risk_manager, risk_management.RiskManager)
        assert currency in Portfolio.available_currencies

        self.cash = initial_holding
        self.total_value = initial_holding
        self.base_currency = currency
        self.assets = {asset.ticker: {'holding': [0.], 'value': [0.], 'asset_data': asset} for asset in assets}
        self.times = []
        self.total_value = []

    def debit(self, amount):
        self.cash += amount

    def credit(self, amount):
        self.cash -= amount

    def update(self, time_series_data):

        total_value = self.cash

        for ticker, asset in self.assets.items():
            if ticker in time_series_data:
                asset['asset_data'].latest_bar = time_series_data[ticker]['bars'][0]
                try:
                    asset['value'] = asset['holding'] * asset['asset_data'].latest_bar.close
                except TypeError:
                    # Catching None
                    asset['value'] = 0
                total_value += asset['value']

        self.times.append(time_series_data['times'])
        self.total_value.append(total_value)

    def self2dict(self):
        data = {
            "total value": self.value_over_time
        }

        return data

    @property
    def value_over_time(self):
        return [(t.strftime("%d-%m-%Y %H:%M:%S"), v) for (t, v) in zip(self.times, self.total_value)]
