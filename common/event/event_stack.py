from common.event import events


class EventStack:

    """
        Container class for holding event objects

    """

    def __init__(self):

        """
        events holds the events in the EventStack
        past_events is a dict used to increment each event type whenever they are popped from the stack. Used in
        analysis later
        """

        self.events = list()
        self.past_events = {
            'time series': 0,
            'market buy signal': 0,
            'market sell signal': 0,
            'limit buy signal': 0,
            'limit sell signal': 0,
            'market buy filled': 0,
            'market sell filled': 0,
            'limit buy filled': 0,
            'limit sell filled': 0,
            'total filled': 0,
            'stop loss': 0,
            'trailing stop': 0
        }

    def add(self, event):
        """
        Method to add an event to the EventStack. The added event can either be a single event or a list of events. If
        they are provided as a list of events, the events in the list are added one by one
        :param event: can either be an event or list of events
        :return: N/A
        """
        if isinstance(event, events.Event) or isinstance(event, events.PendingOrderEvent):
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
        Method that pops the first item in the stack and returns in. Increments the appropriate event type in
        self.past_events dictionary.
        Raises EventStackEmptyError if the event stack is empty

        :return: event. If there are no more events in the even stack, return None and False
        """
        try:
            event = self.events.pop()

            if type(event) == events.TimeSeriesEvent:
                self.past_events['time series'] += 1
            elif type(event) == events.SignalEventMarketBuy:
                self.past_events['market buy signal'] += 1
            elif type(event) == events.SignalEventMarketSell:
                self.past_events['market sell signal'] += 1
            elif type(event) == events.SignalEventLimitBuy:
                self.past_events['limit buy signal'] += 1
            elif type(event) == events.SignalEventLimitSell:
                self.past_events['limit sell signal'] += 1
            elif type(event) == events.OrderFilledEvent:
                if event.type == 'market':
                    if event.side == 'sell':
                        self.past_events['market sell filled'] += 1
                    elif event.side == 'buy':
                        self.past_events['market buy filled'] += 1
                elif event.type == 'limit':
                    if event.side == 'sell':
                        self.past_events['limit sell filled'] += 1
                    elif event.side == 'buy':
                        self.past_events['limit buy filled'] += 1
            elif type(event) == events.StopLossEvent:
                self.past_events['stop loss'] += 1
            elif type(event) == events.TrailingStopEvent:
                self.past_events['trailing stop'] += 1
            elif type(event) == events.OrderFilledEvent:
                self.past_events['total filled'] += 1

            return event
        except IndexError:
            raise EventStackEmptyError

    def report(self):
        return self.past_events


class PostEventStack(EventStack):

    def __init__(self):
        super().__init__()

    def dump(self):
        events = self.events
        self.events = []
        return events


class EventStackEmptyError(Exception):
    pass
