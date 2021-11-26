from shinywaffle.backtesting.backtest import Backtester
from shinywaffle.backtesting.study.test_train_split import TestTrainSplit
from shinywaffle.backtesting.study.uncertainy import UncertaintyVariableManifest
import numpy as np
import pandas as pd
import os
from datetime import datetime
import json
from enum import Enum
from shinywaffle.common.context import Context


class TypeWFA(Enum):
    ROLLING = 'rolling'
    ANCHORED = 'anchored'


class BacktestStudy:

    """
    Class for setting up for a study to allow for many consecutive backtests.
    """
    def __init__(self, context: Context, backtester: Backtester, study_name: str,
                 variable_swap_manifest: UncertaintyVariableManifest, num_runs: int, num_sub_runs: int = 1,
                 num_stochastic_runs: int = 1, save_path: str = os.getcwd(), out_of_sample_size: float = 0.2,
                 wfa=TypeWFA.ROLLING):

        """

        :param context: The context object containing assets, strategies, broker, account
        :param backtester: The default backtester object used to create the copies from
        :param study_name: Name of study
        :param num_runs: Number of runs
        :param num_sub_runs: Number of sub runs
        :param num_stochastic_runs: Number of stochastic runs per sub run
        :param save_path: Path to the root directory for storing backtest simulation results
        :param out_of_sample_size: Percentage of total sample size is used for out of sample simulation
        :param wfa: Walk-forward-analysis method. Either 'anchored' or 'rolling'
        """

        if not isinstance(wfa, TypeWFA):
            raise TypeError('Walk forward analysis must be of type TypeWFA')

        self.context = context
        self._backtest_template = backtester
        self.study_name = study_name
        self.save_path = save_path
        self.no_runs = num_runs
        self.no_sub_runs = num_sub_runs
        self.no_stochastic_runs = num_stochastic_runs
        self.out_of_sample_size = out_of_sample_size
        self.wfa = wfa
        self.total_number_of_runs = self.no_sub_runs * self.no_runs * self.no_stochastic_runs

        self.parameters = list()
        self.sim_paths = list()
        self.backtests = list()
        self.variable_swap_manifest = variable_swap_manifest

        # Creating main study results folder
        self.workflow_run_path = self.save_path + "/" + self.study_name + " " + datetime.now().strftime("%d-%m-%Y %H %M %S")
        os.makedirs(self.workflow_run_path, exist_ok=True)

        # Making tuples with optimisation splits and out of sample splits
        # Tuples consist of from an to splits in terms of percentage of the total data set
        datetime_from = self._backtest_template.times[0]
        datetime_to = self._backtest_template.times[-1]

        test_train_split = TestTrainSplit(self.wfa, self.out_of_sample_size, self.no_sub_runs)
        self._optimisation_datetimes = test_train_split.calc_optimisation_datetimes(datetime_from, datetime_to)
        self._out_of_sample_datetimes = test_train_split.calc_out_of_sample_datetimes(datetime_from, datetime_to)

    @property
    def enable_stochastic(self):
        return True if self.no_stochastic_runs > 1 else False

    def create_results_folder(self, run_no: int, sub_run_no: int, stochastic_run_no: int) -> None:
        """
        Creates the results folders for the summary json files to sit in. Also appends the backtest json file paths
        to the list of simulation paths
        """
        run_path = self.workflow_run_path + "/run_{}".format(run_no)

        # Create one folder per sub run folder under each run folder
        sub_run_path = run_path + "/sub_run_{}".format(sub_run_no)
        if self.enable_stochastic:
            stochastic_run_path = sub_run_path + "_stochastic_{}".format(stochastic_run_no)
            self.sim_paths.append(stochastic_run_path)
        else:
            self.sim_paths.append(sub_run_path)

        os.makedirs(sub_run_path, exist_ok=True)

    def set_uncertainty_parameter_values(self, param_file: str):
        """
        Sets the uncertainty parameters of the study

        :param param_file: Either the name of parameter or a path to a csv file containing a list of param values.
                        Parameter name is them the header in the csv file
        :return:
        """
        # Use pandas to read the csv file and store the values in a dict from there

        df = pd.read_csv(param_file)
        df.dropna(axis=1, how='any', inplace=True)
        for row, values in df.iterrows():
            realization_dict = dict()
            for param_name, param_value in values.items():
                realization_dict[param_name] = param_value
            self.parameters.append(realization_dict)

    def run(self):

        """

        1) Prepare backtest objects
        2) Summarise the folder structure with runs in a json file

        """

        # Preparations
        self.make_backtests()
        self.report()
        for i, backtest in enumerate(self.backtests):
            print('Running backtest {} / {}'.format(i+1, self.total_number_of_runs))
            print('  Run: {}'.format(backtest.run_no+1))
            print('  Sub run: {}'.format(backtest.sub_run_no+1))
            for sim_no, simulation in enumerate(backtest.backtests):
                print('  Stochastic run: {}'.format(sim_no+1))
                simulation['backtest'].run()

    def make_backtests(self):

        """
        This method creates a list of Backtester objects which are later run with the run() method.
        For each run_no, sub_run_no and stochastic_run_no, a results folder is first generated (if it is not already
        in place). Then parameters are drawn from the self.parameters dictionary corresponding to the run_no.

        The context object is copied using deep copy to break all pointers and then the substitute_uncertainty_variable
        method is called on new_context.strategies, new_context.risk_manager and new_context.account to substitute all
        UncertaintyVariable objects with the appropriate variable value collected from the self.parameters dictionary.

        A new Backtester object is then created with the new_context object and the new backtest_from and backtest_to
        times calculated from the test_train_split method. The slippages in the broker object have to be drawn from the
        normal distribution again and injected into the new_context.broker object. A BacktesterContainer object
        is created with the new Backtester object and is appended to the list of backtests.
        """

        for run_no in range(self.no_runs):
            params = self.parameters[run_no]
            self.variable_swap_manifest.perform_swaps(realization=params)
            for sub_run_no in range(self.no_sub_runs):
                path = self.workflow_run_path + "/run_{}".format(run_no) + "/sub_run_{}".format(sub_run_no)
                run_from = self._optimisation_datetimes[sub_run_no][0]
                run_to = self._optimisation_datetimes[sub_run_no][1]
                name = f"run_{run_no} sub_run_{sub_run_no}"
                backtest_container = BacktestContainer(name=name, parameters=params,
                                                       run_no=run_no, sub_run_no=sub_run_no)
                for stochastic_run_no in range(self.no_stochastic_runs):
                    self.create_results_folder(run_no=run_no,
                                               sub_run_no=sub_run_no,
                                               stochastic_run_no=stochastic_run_no)
                    if self.enable_stochastic:
                        name = f"run_{run_no} sub_run_{sub_run_no} stochastic_{stochastic_run_no}"

                    # Deep copy
                    new_context = self.context.copy()

                    # The slippages have to be re-drawn to avoid using the same slippage values in every run
                    new_context.broker.slippages = abs(np.random.normal(new_context.broker._slippage_mean,
                                                                        new_context.broker._slippage_stdev,
                                                                        100000)).tolist()

                    new_backtester = Backtester(context=new_context,
                                                time_increment=self._backtest_template.time_increment,
                                                run_from=run_from, run_to=run_to, path=path, filename=name)

                    result_path = f'{new_backtester.reporter.path}/{name}.json'
                    backtest_container.add_backtest(backtest=new_backtester,
                                                    result_path=result_path)
                self.backtests.append(backtest_container)

    def report(self):
        data = {
            'name': self.study_name,
            'path': self.save_path,
            'number of runs': self.no_runs,
            'number of sub runs': self.no_sub_runs,
            'number of stochastic runs': self.no_stochastic_runs,
            'total number of runs': self.total_number_of_runs,
            'walk-forward analysis': self.wfa.value,
            'out of sample size': self.out_of_sample_size,
            'optimisation datetimes': [(d[0].strftime("%d-%m-%Y %H:%M:%S"), d[1].strftime("%d-%m-%Y %H:%M:%S"))
                                       for d in self._optimisation_datetimes],
            'out of sample datetimes': [(d[0].strftime("%d-%m-%Y %H:%M:%S"), d[1].strftime("%d-%m-%Y %H:%M:%S"))
                                        for d in self._out_of_sample_datetimes],
            'swappable_parameters': [sp.name for sp in self.variable_swap_manifest.swappables],
            'runs': [b.report() for b in self.backtests]
        }

        # Dump as json to file
        with open(self.workflow_run_path + "/workflow_summary.json", "w") as json_out:
            json.dump(data, json_out, sort_keys=True, indent=4)


class BacktestContainer:
    def __init__(self, name: str, parameters: dict, run_no: int, sub_run_no: int):
        self.name = name
        self.parameters = parameters
        self.run_no = run_no
        self.sub_run_no = sub_run_no
        self.backtests = list()

    def add_backtest(self, backtest: Backtester, result_path: str) -> None:
        self.backtests.append({
            'backtest': backtest,
            'result_path': result_path
        })

    def stochastic_result_path(self, backtest: Backtester):
        return f'{backtest.reporter.save_path}/{backtest.reporter.filename}.json'

    def report(self):
        return {
            'name': self.name,
            'parameters': self.parameters,
            'run number': self.run_no,
            'sub run number': self.sub_run_no,
            'runs': [s['result_path'] for s in self.backtests]
        }
