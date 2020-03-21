import abc


class API(abc.ABC):

    """
    Base class for REST API classes

    """

    def __init__(self, token):
        self.token = token
