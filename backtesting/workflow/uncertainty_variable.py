"""
Class holding uncertainty variables and is used to locate varying factors in workflow runs
"""


class UncertaintyVariable:

    def __init__(self, param_name):

        self.param_name = param_name
