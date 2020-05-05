import random
import numpy as np
import math as m


def generate_high_low_times(dt, total_t):
    n = round(total_t/dt)
    boundary_distance = 0.2
    if 0 <= random.random() < 0.5:
        # Bar low point comes before high point
        low_t = min(n * boundary_distance, m.floor((n-1) * random.random()))
        n -= low_t
        high_t = low_t + min(n * (1-boundary_distance), m.floor((n-1) * random.random()))

    else:
        # High comes before high
        high_t = min(n * boundary_distance, m.floor((n-1) * random.random()))
        n -= high_t
        low_t = high_t + min(n * (1-boundary_distance), m.floor((n-1) * random.random()))

    low_t = low_t / round(total_t/dt)
    high_t = high_t / round(total_t/dt)
    return high_t, low_t, 0, 1


def interp_price_with_noise(s_start, s_end, dt, total_t, sigma, constraints):
    s = []
    n = round(total_t/dt)
    noise = np.random.normal(0., sigma, int(n))

    min_constraint = min(constraints)
    max_constraint = max(constraints)

    for i in range(n):
        if i == 0:
            s_new = s_start
        else:
            s_new = s[-1] + (s_end - s_start) / n

            if s_new + noise[i] > max_constraint:
                s_new -= abs(noise[i])
            elif s_new + noise[i] < min_constraint:
                s_new += abs(noise[i])
            else:
                s_new += noise[i]
        s.append(s_new)
    return s


def simulate_intrabar_data(bar, total_t, dt=0.01, stdev_dampening=20, sigma=None):

    class PricePoint:
        def __init__(self, value, T):
            self.value = value
            self.T = T

        def __repr__(self):
            return '{} at {}'.format(self.value, self.T)

    if not sigma:
        sigma = np.std([bar.low, bar.high, bar.close, bar.open]) / stdev_dampening

    high_t, low_t, open_t, close_t = generate_high_low_times(dt, total_t)
    price_points = sorted([PricePoint(bar.high, high_t),
                           PricePoint(bar.low, low_t),
                           PricePoint(bar.open, open_t),
                           PricePoint(bar.close, close_t)
                           ], key=lambda b: b.T)

    s = []
    for i in range(len(price_points)-1):
        s_start = price_points[i].value
        s_end = price_points[i+1].value
        constraints = [bar.high, bar.low]

        s += interp_price_with_noise(s_start, s_end, dt, total_t, sigma, constraints)

    s.append(bar.close)
    return s