import copy


class Context:

    """
    Context class representing a holder for assets, broker and account. This object will be
    """

    assets = {}

    @classmethod
    def add_asset(cls, ticker, asset):
        Context.assets[ticker] = asset

    @classmethod
    def copy(cls):
        return copy.deepcopy(cls)
