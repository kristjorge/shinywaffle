"""
Class holding uncertainty variables and is used to locate varying factors in workflow runs
"""


class UncertaintyContext:

    def __init__(self):
        self.variables = []

    def set_variables(self, *others):
        for other in others:
            if other not in self.variables:
                self.variables.append(other)


class UncertaintyVariable:

    def __init__(self, param_name):
        self.param_name = param_name

