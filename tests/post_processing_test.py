from shinywaffle.backtesting.backtesting_result import BacktestEnsemble
from matplotlib import pyplot as plt


def main():
    ensemble = BacktestEnsemble(json_path="C:\PythonProjects\shiny-waffle\simulations\Simple SMA study sample  24-11-2021 23 06 19\workflow_summary.json")

    fig, ax = plt.subplots(figsize=(16, 9))
    all_times = list()

    for realization in ensemble.realizations:
        for run in realization.runs:
            times = run.times[1:]
            values = run.account.values[1:]
            all_times.append(times)

            ax.plot(times, values)

    plt.show()



if __name__ == '__main__':
    main()