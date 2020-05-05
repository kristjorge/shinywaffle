import json
from matplotlib import pyplot as plt


def main(file_path):
    with open(file_path, 'r') as data_file:
        data_dict = json.load(data_file)

    account = data_dict['account']
    cash = account['cash']
    total_value = account['total value']
    times = account['times']

    plt.plot(cash)
    plt.plot(total_value)
    plt.show()


if __name__ == '__main__':
    main('D:/PythonProjects/shiny-waffle/tests/Summary 05-05-2020 205143.json')
