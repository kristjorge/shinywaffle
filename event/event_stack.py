from event.event import Event

"""
Container class for holding event objects

"""


class EventStack:

    def __init__(self):
        self.events = list()

    def add(self, event):
        if isinstance(event, Event):
            self.events.append(event)
        elif isinstance(event, list):
            for e in event:
                self.events.append(e)

    def get(self):
        """

        :return: event and True. If there are no more events in the even stack, return None and False
        """
        try:
            event = self.events.pop()
            return event
        except IndexError:
            raise EventStackEmptyError


class EventStackEmptyError(Exception):
    """ EventStack is empty"""
    pass
