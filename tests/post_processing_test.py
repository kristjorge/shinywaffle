import json
from matplotlib import pyplot as plt


def main(file_path):
    with open(file_path, 'r') as data_file:
        data_dict = json.load(data_file)

    account = data_dict['account']
    cash = account['cash']
    total_value = account['total value']
    times = account['times']
    positions = account['positions']

    for id, position in positions.items():
        values = position['time series']['value']
        plt.plot(values)

        plt.show()


if __name__ == '__main__':
    main('D:/PythonProjects/shiny-waffle/tests/Summary 05-05-2020 205934.json')
