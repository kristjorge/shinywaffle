"""

Class holding the initial holding in a base currency for the backtesting

"""


class Portfolio:

    available_currencies = ("USD", "NOK", "GBP", "EUR")

    def __init__(self, holding, currency):
        self.holding = holding
        assert currency in Portfolio.available_currencies
        self.base_currency = currency

    def debit(self, amount):
        self.holding += amount

    def credit(self, amount):
        self.holding -= amount
