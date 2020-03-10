import abc

"""
Base class for events
"""


class Event(abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        pass