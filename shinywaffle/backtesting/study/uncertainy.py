from typing import Union, List


class UncertaintyVariable:
    def __init__(self, name: str):
        """
        Names uncertainty variable. Inserted instead of the actual value in the object that will have it's variable
        value changed in a backtest study.

        The name is used to link the uncertainty value in the manifest to the value in the realization dict.
        """
        self.name = name

    def __repr__(self):
        return f'Uncertainty variable with name {self.name}'


class UncertaintyVariableSwappable:
    def __init__(self, parent_obj: object, attr_name: str, name: str):
        """
        Class for holding a swappable uncertainty variable. This is used to hold the parent object that will have
        its attribute swapped, the name of the attribute that will be swapped and the named uncertainty variable
        """
        self.parent_obj = parent_obj
        self.attr_name = attr_name
        self.name = name


class UncertaintyVariableManifest:
    """
    The manifest containing all the swappable uncertainty variables in the study. This is used to perform the
    actual attribute swaps, swapping the uncertainty variable for the actual value in the manifest
    """
    def __init__(self):
        self.swappables = list()

    def add_swappable(self, swappable: Union[List[UncertaintyVariableSwappable], UncertaintyVariableSwappable]):
        """ Adds a UncertaintyVariableSwappable to the list of swappables"""
        if isinstance(swappable, UncertaintyVariableSwappable):
            self.swappables.append(swappable)
        if isinstance(swappable, list):
            for s in swappable:
                self.swappables.append(s)

    def perform_swaps(self, realization: dict):
        """
        Performs the actual swapping of the variables.
        Gets the value from the realization dictionary and then sets the attribute (attr_name) in the parent object
        to the value of the realization value
        """
        for swappable in self.swappables:
            realization_value = realization[swappable.name]
            setattr(swappable.parent_obj, swappable.attr_name, realization_value)
