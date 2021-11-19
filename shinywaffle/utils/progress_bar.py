import sys
import math


class ProgressBar:
    def __init__(self, steps):
        self.steps = steps
        self.counter = 0
        self.last_step = 0
        self.initial_string = '[%s] 0%% (%i / %i steps completed)' % (' ' * 100, 0, self.steps)
        sys.stdout.write(self.initial_string)
        sys.stdout.flush()

    @property
    def percentage_complete(self):
        return math.floor(100 * self.counter / self.steps)

    def update(self):
        self.counter += 1
        self.last_step += 1
        sys.stdout.write('\b' * (len(self.initial_string)+1))
        new_string_out = '[%s%s] %i%% (%i / %i steps completed)' % ('#' * self.percentage_complete,
                                                            ' ' * (100 - self.percentage_complete),
                                                                self.percentage_complete,
                                                                self.last_step, 
                                                                self.steps)
        sys.stdout.write(new_string_out)
        self.initial_string = new_string_out
        sys.stdout.flush()

        if self.percentage_complete == 100:
            sys.stdout.write('\n')

