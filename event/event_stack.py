from event import events


class EventStack:

    """
        Container class for holding event objects

    """

    def __init__(self):
        self.events = list()
        self.past_events = {
            'time series': 0,
            'buy signal': 0,
            'sell signal': 0,
            'buy limit order': 0,
            'sell limit order': 0,
            'buy market order': 0,
            'sell market order': 0,
            'stop loss': 0,
            'trailing stop': 0,
            'order filled': 0
        }
        # self.past_events = {
        #     repr(events.TimeSeriesEvent): 0,
        #     repr(events.SignalEventBuy): 0,
        #     repr(events.SignalEventSell): 0,
        #     repr(events.LimitOrderBuyEvent): 0,
        #     repr(events.LimitOrderSellEvent): 0,
        #     repr(events.MarketOrderBuyEvent): 0,
        #     repr(events.MarketOrderSellEvent): 0,
        #     repr(events.StopLossEvent): 0,
        #     repr(events.TrailingStopEvent): 0,
        #     repr(events.OrderFilledEvent): 0
        # }

    def add(self, event):
        if isinstance(event, events.Event):
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
            # self.past_events[str(event)] += 1

            if type(event) == events.TimeSeriesEvent:
                self.past_events['time series'] += 1
            elif type(event) == events.SignalEventBuy:
                self.past_events['buy signal'] += 1
            elif type(event) == events.SignalEventSell:
                self.past_events['sell signal'] += 1
            elif type(event) == events.LimitOrderBuyEvent:
                self.past_events['buy limit order'] += 1
            elif type(event) == events.LimitOrderSellEvent:
                self.past_events['sell limit order'] += 1
            elif type(event) == events.MarketOrderBuyEvent:
                self.past_events['buy market order'] += 1
            elif type(event) == events.MarketOrderSellEvent:
                self.past_events['sell market order'] += 1
            elif type(event) == events.StopLossEvent:
                self.past_events['stop loss'] += 1
            elif type(event) == events.TrailingStopEvent:
                self.past_events['trailing stop'] += 1
            elif type(event) == events.OrderFilledEvent:
                self.past_events['order filled'] += 1

            return event
        except IndexError:
            raise EventStackEmptyError

    def self2dict(self):
        return self.past_events

class EventStackEmptyError(Exception):
    # EventStack is empty
    pass

#     'stop loss': 0,
#     'trailing stop': 0,
#     'order filled': 0
# }