import sys
import math


class ProgressBar:
    def __init__(self, steps):
        self.steps = steps
        self.counter = 0
        self.initial_string = '[%s] 0%% (0.0 seconds)' % (' ' * 100)
        sys.stdout.write(self.initial_string)
        sys.stdout.flush()

    @property
    def percentage_complete(self):
        return math.floor(100 * self.counter / self.steps)

    def update(self):
        self.counter += 1
        sys.stdout.write('\b' * (len(self.initial_string)+1))
        sys.stdout.write('[%s%s] %i%%' % ('#' * self.percentage_complete,
                                          ' ' * (100 - self.percentage_complete),
                                          self.percentage_complete))
        sys.stdout.flush()

        if self.percentage_complete == 100:
            sys.stdout.write('\n')

