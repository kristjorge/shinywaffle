
"""
Container class for holding event objects

"""


class EventStack:

    def __init__(self):
        self.events = list()

    def add(self, event):
        self.events.append(event)

    def get(self):
        """

        :return: event and True. If there are no more events in the even stack, return None and False
        """

        if self.events:
            event = self.events.pop()
            return event, True
        else:
            return None, False

    @property
    def empty(self):
        if self.events:
            return True
        else:
            return False
