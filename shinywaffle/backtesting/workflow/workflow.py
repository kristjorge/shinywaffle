from backtesting.backtest import Backtester, BacktestContainer
from backtesting.workflow.test_train_split import TestTrainSplit
from backtesting.workflow.uncertainty_variable import UncertaintyVariable
from data.bar import Bar
from data.time_series_data import TimeSeries
import numpy as np
import pandas as pd
import os
import types
from datetime import datetime, timedelta
import json

skippable_types = (str,
                   float,
                   int,
                   datetime,
                   timedelta,
                   types.BuiltinMethodType,
                   types.BuiltinFunctionType,
                   Bar,
                   TimeSeries)


class BacktestWorkflow:

    """
    Class for setting up for a workflow to allow for many consecutive backtests.

    """

    wfa_types = ("rolling", "anchored")

    def __init__(self, context, backtester, name, runs, sub_runs=1, stochastic_runs=1, path=os.getcwd(),
                 out_of_sample_size=0.2, wfa='rolling'):

        """

        :param context: The context object containing assets, strategies, broker, account
        :param backtester: The default backtester object used to create the copies from
        :param name: Name of workflow
        :param runs: Number of runs
        :param sub_runs: Number of sub runs
        :param stochastic_runs: Number of stochastic runs per sub run
        :param path: Path to the root directory for storing backtest simulation results
        :param out_of_sample_size: Percentage of total sample size is used for out of sample simulation
        :param wfa: Walk-forward-analysis method. Either 'anchored' or 'rolling'
        """

        assert isinstance(wfa, str) and wfa in BacktestWorkflow.wfa_types
        assert isinstance(runs, int) and runs > 0
        assert isinstance(sub_runs, int) and sub_runs > 0
        assert isinstance(stochastic_runs, int) and stochastic_runs > 0

        self.context = context
        self._backtester = backtester
        self.workflow_name = name
        self.path = path
        self.no_runs = runs
        self.no_sub_runs = sub_runs
        self.no_stochastic_runs = stochastic_runs
        self.out_of_sample_size = out_of_sample_size
        self.wfa = wfa
        self.total_number_of_runs = self.no_sub_runs * self.no_runs * self.no_stochastic_runs
        self.enable_stochastic = True if stochastic_runs > 1 else False
        self.parameters = dict()
        self.sim_paths = list()
        self.backtests = list()
        self.subbed_parameters = list()

        # Creating main workflow results folder
        self.workflow_run_path = self.path + "/" + self.workflow_name + " " + datetime.now().strftime("%d-%m-%Y %H %M %S")
        os.mkdir(self.workflow_run_path)

        # Making tuples with optimisation splits and out of sample splits
        # Tuples consist of from an to splits in terms of percentage of the total data set
        datetime_from = self._backtester.times[0]
        datetime_to = self._backtester.times[-1]

        test_train_split = TestTrainSplit(self.wfa, self.out_of_sample_size, self.no_sub_runs)
        self._optimisation_datetimes = test_train_split.calc_optimisation_datetimes(datetime_from, datetime_to)
        self._out_of_sample_datetimes = test_train_split.calc_out_of_sample_datetimes(datetime_from, datetime_to)

    def create_results_folder(self, run_no, sub_run_no, stoch_run_no):
        run_path = self.workflow_run_path + "/run_{}".format(run_no)
        if not os.path.isdir(run_path):
            os.mkdir(run_path)

        # Create one folder per sub run folder under each run folder
        sub_run_path = run_path + "/sub_run_{}".format(sub_run_no)
        if self.enable_stochastic:
            stoch_run_path = sub_run_path + "_stochastic_{}".format(stoch_run_no)
            self.sim_paths.append(stoch_run_path)
        else:
            self.sim_paths.append(sub_run_path)

        if not os.path.isdir(sub_run_path):
            os.mkdir(sub_run_path)

    def set_uncertainty_parameter_values(self, param, values=None):

        """

        :param param: Either the name of parameter or a path to a csv file containing a list of param values.
                        Parameter name is them the header in the csv file
        :param values: List of values. If not specified (None) the path in param is used to read the csv file using
                        Pandas.
        :return:
        """

        assert isinstance(param, str)
        if values is not None:
            # If the list of values is specified it is saved in the dict
            assert isinstance(values, list), "Value must be provided as a list"
            assert len(values) == self.no_runs, "List of values must match the number of runs"
            self.parameters[param] = values

        else:
            # Use pandas to read the csv file and store the values in a dict from there
            df = pd.read_csv(param)
            df.dropna(axis=1, how='any', inplace=True)
            for col, values in df.iteritems():
                self.parameters[col] = list(values)

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
            print('  Stochastic run: {}'.format(backtest.stochastic_run_no+1))
            backtest.backtester.run()

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

        Lastly a check is made to see which (if any) uncertainty variables are not substituted out. If any, they are
        removed from the parameters dictionary and will not be reported in the final workflow json output.
        """

        for run_no in range(self.no_runs):
            for sub_run_no in range(self.no_sub_runs):
                for stochastic_run_no in range(self.no_stochastic_runs):

                    self.create_results_folder(run_no, sub_run_no, stochastic_run_no)

                    params = {p: p_value[run_no] for p, p_value in self.parameters.items()}
                    path = self.workflow_run_path + "/run_{}".format(run_no) + "/sub_run_{}".format(sub_run_no)
                    backtest_from = self._optimisation_datetimes[sub_run_no][0]
                    backtest_to = self._optimisation_datetimes[sub_run_no][1]
                    name = "run_{} sub_run_{}".format(run_no, sub_run_no)

                    if self.enable_stochastic:
                        name += " stochastic_{}".format(stochastic_run_no)

                    # Deep copy
                    new_context = self.context.copy()
                    self.substitute_uncertainty_variable(new_context.strategies, run_no)
                    self.substitute_uncertainty_variable(new_context.risk_manager, run_no)
                    self.substitute_uncertainty_variable(new_context.account, run_no)

                    # The slippages have to be re-drawn to avoid using the same slippage values in every run
                    new_context.broker.slippages = abs(np.random.normal(0, 0.05, 100000)).tolist()

                    new_backtester = Backtester(new_context, self._backtester.time_increment, backtest_from,
                                                backtest_to, path, name)

                    # Append to list of backtests
                    self.backtests.append(BacktestContainer(name, params, new_backtester,
                                                            path, run_no, sub_run_no, stochastic_run_no))

        # Check that all parameters provided in list of parameters are actually subbed out
        to_be_removed = list()
        for param_name in self.parameters:
            if param_name not in self.subbed_parameters:
                print("{} was provided in the list of parameters, but never substituted "
                      " into a backtest".format(param_name))
                print("{} was deleted from the parameters list".format(param_name))
                to_be_removed.append(param_name)

        for p in to_be_removed:
            del self.parameters[p]

    def substitute_uncertainty_variable(self, obj, param_no):

        attributes = [a for a in dir(obj) if not a.startswith("_")
                      and a not in dir("__builtins__")
                      and not hasattr(getattr(obj, a), '__call__')
                      and not a == 'context' and not a == 'account' and not a == 'broker']

        if attributes:
            for attr in attributes:
                new_obj = getattr(obj, attr)
                new_obj_type = type(new_obj)

                # If uncertainty value then substitute the object with a value from the dictionary
                if new_obj_type == UncertaintyVariable:
                    variable_name = new_obj.param_name
                    variable_value = self.parameters[variable_name][param_no]
                    setattr(obj, attr, variable_value)

                    # Returns the name of the variable substituted
                    self.subbed_parameters.append(new_obj.param_name)

                # If a list or a tuple
                # Run substitution recursion on all items in list / tuple
                elif new_obj_type == list or new_obj_type == tuple:
                    for i in new_obj:
                        self.substitute_uncertainty_variable(i, param_no)

                # if dict
                # Run substitution recursion on all values in dictionary
                elif new_obj_type == dict:
                    for key, value in new_obj.items():
                        self.substitute_uncertainty_variable(value, param_no)

                elif isinstance(new_obj, skippable_types):
                    continue

                else:
                    self.substitute_uncertainty_variable(new_obj, param_no)
        elif type(obj) == dict:
            for item in obj.values():
                self.substitute_uncertainty_variable(item, param_no)

        elif type(obj) == list:
            for item in obj:
                self.substitute_uncertainty_variable(item, param_no)

    def report(self):
        data = {
            'name': self.workflow_name,
            'path': self.path,
            'number of runs': self.no_runs,
            'number of sub runs': self.no_sub_runs,
            'number of stochastic runs': self.no_stochastic_runs,
            'total number of runs': self.total_number_of_runs,
            'walk-forward analysis': self.wfa,
            'out of sample size': self.out_of_sample_size,
            'optimisation datetimes': [(d[0].strftime("%d-%m-%Y %H:%M:%S"), d[1].strftime("%d-%m-%Y %H:%M:%S"))
                                       for d in self._optimisation_datetimes],
            'out of sample datetimes': [(d[0].strftime("%d-%m-%Y %H:%M:%S"), d[1].strftime("%d-%m-%Y %H:%M:%S"))
                                        for d in self._out_of_sample_datetimes],
            'parameters': {param: param_values for param, param_values in self.parameters.items()},
            'runs': [b.report() for b in self.backtests]
        }

        # Dump as json to file
        with open(self.workflow_run_path + "/workflow_summary.json", "w") as json_out:
            json.dump(data, json_out, sort_keys=True, indent=3)
