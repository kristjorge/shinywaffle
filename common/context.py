import copy


class Context:

    """
    Context class representing a holder for assets, broker and account. This object will be
    """

    def __init__(self):
        from data.time_series_data import RetrievedTimeSeriesData
        self.assets = {}
        self.broker = None
        self.account = None
        self.retrieved_data = RetrievedTimeSeriesData(self)

    def copy(self):
        return copy.deepcopy(self)
