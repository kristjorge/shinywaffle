import json
from datetime import datetime
from collections import defaultdict
from shinywaffle.backtesting import DATETIME_FORMAT


def parse_positions(data: dict) -> dict:
    parsed_positions = defaultdict(lambda: list())
    for ticker, positions in data.items():
        for position in positions:
            parsed_positions[ticker].append(ResultPosition(data=position))

    return parsed_positions


class ResultTransaction:
    def __init__(self, data: dict):
        self.volume = data['volume']
        self.price = data['price']
        self.size = data['size']
        self.side = data['side']
        self.time = datetime.strptime(data['time'], DATETIME_FORMAT)


class ResultPosition:
    def __init__(self, data: dict):
        self.id = data['id']
        self.opened_time = datetime.strptime(data['opened_time'], DATETIME_FORMAT)
        try:
            self.closed_time = datetime.strptime(data['closed_time'], DATETIME_FORMAT)
        except TypeError:
            self.closed_time = None

        self.enter_price = data['enter_price']
        self.avg_close_price = data['avg_close_price']
        self.total_return = data['total_return']
        self.total_buy_size = data['total_buy_size']
        self.total_sell_size = data['total_sell_size']
        self.total_return_percent = data['total_return_percent']
        self.values = data['values']
        self.returns = data['returns']
        self.maximum_drawdown = data['maximum_drawdown']
        self.days_in_trade = data['days_in_trade']
        self.hours_in_trade = data['hours_in_trade']
        self.minutes_in_trade = data['minutes_in_trade']
        self.times = [datetime.strptime(t, DATETIME_FORMAT) for t in data['times']]
        self.volumes = data['volumes']
        self.transactions = [ResultTransaction(data=d) for d in data['transactions']]
        self.num_transactions = data['num_transactions']
        try:
            self.closed = datetime.strptime(data['closed'], DATETIME_FORMAT)
        except ValueError:
            self.closed = None


class DictResultHolder:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

class ResultAccount:
    def __init__(self, data: dict):
        self.trades = [DictResultHolder(data=t) for t in data['trades']]
        self.values = data['values']
        self.total_return = data['return']
        self.total_return_percent = data['return_percent']
        self.returns = data['returns']
        self.returns_percen = data['returns_percent']
        self.maximum_drawdown = data['maximum_drawdown']
        self.base_balances = data['base_balances']
        self.active_trades = data['active_trades']
        self.balances = data['balances']
        self.positions = parse_positions(data=data['positions'])
        self.num_winning_positions = data['num_winning_positions']
        self.num_losing_positions = data['num_losing_positions']
        self.frac_winning_positions = data['frac_winning']
        self.avg_win_return = data['avg_win_return']
        self.avg_win_return_percent = data['avg_win_return_percent']
        self.avg_los_return = data['avg_los_return']
        self.avg_los_return_percent = data['avg_los_return_percent']


class BacktestingResult:
    def __init__(self, json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(fp=f)

        self.broker = DictResultHolder(data=data['broker'])
        self.assets = data['assets']
        self.strategies = data['strategies']
        self.backtest_from = datetime.strptime(data['backtest_from'], DATETIME_FORMAT)
        self.backtest_to = datetime.strptime(data['backtest_to'], DATETIME_FORMAT)
        self.times = [datetime.strptime(dt, DATETIME_FORMAT) for dt in data['times']]
        self.events = DictResultHolder(data=data['events'])
        self.account = ResultAccount(data=data['account'])




