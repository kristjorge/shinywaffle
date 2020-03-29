from event.events import Event


class EventStack:

    """
        Container class for holding event objects

    """

    def __init__(self):
        self.events = list()

    def add(self, event):
        if isinstance(event, Event):
            if event is not None:
                self.events.append(event)
            else:
                pass

        elif isinstance(event, list):
            for e in event:
                if e is not None:
                    self.events.append(e)
                else:
                    continue

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
    # EventStack is empty
    pass
