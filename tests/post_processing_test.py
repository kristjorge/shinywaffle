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

    plt.plot(total_value)
    plt.show()


if __name__ == '__main__':
    main('C:\PythonProjects\shiny-waffle\Summary 16-01-2021 210100.json')
