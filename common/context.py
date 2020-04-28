import copy


class Context:

    """
    Context class representing a holder for assets, broker and account. This object will be
    """

    def __init__(self):
        self.assets = {}
        self.broker = None
        self.account = None
        self.time_series_data = None

    def copy(self):
        return copy.deepcopy(self)
