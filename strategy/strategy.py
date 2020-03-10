import abc
from backtesting.workflow.uncertainty_variable import UncertaintyVariable

""" 

Base class for trading strategies used in either backtesting or live trading.
All implemented strategies must inherit from this super class 

Functions:
    - read: Returns the TradingStrategy object 
    - generate_signal: Evaluates data and generates a signal either "buy" or "sell"


"""


class TradingStrategy(abc.ABC):

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def generate_signal(self):
        pass

    def set_param_value(self, param, value):
        setattr(self, param, value)


