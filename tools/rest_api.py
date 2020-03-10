import abc

"""
Base class for REST API classes

"""


class API(abc.ABC):

    def __init__(self, token):
        self.token = token

