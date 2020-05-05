import json

with open('D:/PythonProjects/shiny-waffle/tests/Summary 05-05-2020 090719.json', 'r') as data_file:
    data_dict = json.load(data_file)


account = data_dict['account']
cash = account['cash']
total_value = account['total value']
times = account['times']

