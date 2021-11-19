from typing import List
from pytest import approx


def drawdown(values: List[float]) -> float:
    """ Calculates the maximum drawdown of a series of values"""
    max_dd = 0
    for i, v in enumerate(values):
        peak = max(values[:i+1])
        dd = v/peak - 1
        if dd <= max_dd:
            max_dd = dd

    return max_dd


def test_drawdown():
    values = [100, 105, 110, 115, 110, 105, 110, 120, 140, 135]
    dd = drawdown(values)
    assert dd == approx(105/115 - 1)


if __name__ == '__main__':
    test_drawdown()