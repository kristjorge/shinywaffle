from datetime import timedelta, datetime
from typing import List, Tuple


class TestTrainSplit:

    def __init__(self, wfa, out_of_sample_size: float, no_sub_runs: int):
        """
        Class for calculating the train test splits of datetime ranges used in backtests.

        :param wfa: Walk forward analysis type
        :param out_of_sample_size: The fraction of the total simulation time that is dedicated to out of sample testing
        :param no_sub_runs: The number of sub runs in the simulation. A sub run is backtest on part of the total
        in sample test range which is created using one of the two types of WFA
        :param optimization_splits: are the split points [0, 1] of the entire in sample testing range that correspond
        to a sub run
        :param optimization_datetimes: The from and to datetimes corresponding to the optimziation_splits for the
        datetime range of the in sample range
        :param out_of_sample_splits: Correspondingly for out of sample split values
        : param out_of_sample_datetimes: Correspondingly for out of sample datetimes


        """
        self.wfa = wfa
        self.out_of_sample_size = out_of_sample_size
        self.no_sub_runs = no_sub_runs
        self.optimisation_splits = None
        self.optimisation_datetimes = None
        self.out_of_sample_splits = None
        self.out_of_sample_datetimes = None
        self.calc_optimisation_splits()
        self.calc_out_of_sample_splits()

    def calc_optimisation_splits(self) -> None:
        """
        Calculates the split fractions [0, 1] for the optimization time periods, either for TypeWFA anchored
        or rolling.

        Rolling TypeWFA means that the time periods are of equal lengths and are moving along the time range
        Anchored TypeWFA means that the time periods always start at the same place and get progressively longer
        """
        from shinywaffle.backtesting.study.study import TypeWFA
        splits = list()
        in_sample_testing = 1 - self.out_of_sample_size
        sub_run_test_size = in_sample_testing / self.no_sub_runs
        if self.wfa == TypeWFA.ROLLING:
            for sub_run_no in range(self.no_sub_runs):
                splits.append(
                    (sub_run_no*sub_run_test_size, (1+sub_run_no)*sub_run_test_size)
                )

        elif self.wfa == TypeWFA.ANCHORED:
            for sub_run_no in range(self.no_sub_runs):
                splits.append(
                    (0, (1+sub_run_no)*sub_run_test_size)
                )

        self.optimisation_splits = splits

    def calc_out_of_sample_splits(self) -> None:
        """
        Calculates the fractions [0, 1] for the out of sample period.
        """

        splits = list()
        in_sample_testing = 1 - self.out_of_sample_size
        sub_run_test_size = in_sample_testing / self.no_sub_runs

        # Out of sample splits are the same for rolling and anchored testing
        for sub_run_no in range(self.no_sub_runs):
            splits.append(
                ((1+sub_run_no)*sub_run_test_size, (1+sub_run_no)*sub_run_test_size + self.out_of_sample_size)
            )

        self.out_of_sample_splits = splits

    def calc_optimisation_datetimes(self, date_from: datetime, date_to: datetime) -> List[Tuple[datetime, datetime]]:
        """
        Calculates the datetimes ranges for each of the sub runs using the specified TypeWFA.
        :param date_from: The datetime from which the sub run starts
        :param date_to: The datetime to which the sub run runs

        Returns a list of datetime tuples
        """
        dt = date_to - date_from
        optimisation_datetimes = list()

        for split in self.optimisation_splits:
            from_split = split[0]
            to_split = split[1]
            optimisation_datetimes.append(
                ((date_from + timedelta(days=from_split * dt.days)),
                 (date_from + timedelta(days=to_split * dt.days)))
            )

        self.optimisation_datetimes = optimisation_datetimes
        return optimisation_datetimes

    def calc_out_of_sample_datetimes(self, date_from: datetime, date_to: datetime) -> List[Tuple[datetime, datetime]]:
        """
        Calculates the datetime ranges for the out of sample time period
        """
        dt = date_to - date_from
        out_of_sample_datetimes = list()

        for split in self.out_of_sample_splits:
            from_split = split[0]
            to_split = split[1]
            out_of_sample_datetimes.append(
                ((date_from + timedelta(days=from_split * dt.days)),
                 (date_from + timedelta(days=to_split * dt.days)))
            )
        self.out_of_sample_datetimes = out_of_sample_datetimes
        return out_of_sample_datetimes
