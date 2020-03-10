from datetime import datetime
from datetime import date
from datetime import timedelta


class TestTrainSplit:

    def __init__(self, wfa, out_of_sample_size, no_sub_runs):
        self.wfa = wfa
        self.out_of_sample_size = out_of_sample_size
        self.no_sub_runs = no_sub_runs
        self.optimisation_splits = None
        self.optimisation_datetimes = None
        self.out_of_sample_splits = None
        self.out_of_sample_datetimes = None
        self.calc_optimisation_splits()
        self.calc_out_of_sample_splits()

    def calc_optimisation_splits(self):
        splits = list()
        in_sample_testing = 1 - self.out_of_sample_size
        sub_run_test_size = in_sample_testing / self.no_sub_runs
        if self.wfa == 'rolling':
            for sub_run_no in range(self.no_sub_runs):
                splits.append(
                    (sub_run_no*sub_run_test_size, (1+sub_run_no)*sub_run_test_size)
                )

        elif self.wfa == 'anchored':
            for sub_run_no in range(self.no_sub_runs):
                splits.append(
                    (0, (1+sub_run_no)*sub_run_test_size)
                )

        self.optimisation_splits = splits

    def calc_out_of_sample_splits(self):

        splits = list()
        in_sample_testing = 1 - self.out_of_sample_size
        sub_run_test_size = in_sample_testing / self.no_sub_runs

        # Out of sample splits are the same for rolling and anchored testing
        for sub_run_no in range(self.no_sub_runs):
            splits.append(
                ((1+sub_run_no)*sub_run_test_size, (1+sub_run_no)*sub_run_test_size + self.out_of_sample_size)
            )

        self.out_of_sample_splits = splits

    def calc_optimisation_datetimes(self, date_from, date_to):
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

    def calc_out_of_sample_datetimes(self, date_from, date_to):
        dt = date_to - date_from
        out_of_sample_datetimes = list()

        for split in self.out_of_sample_splits:
            from_split = split[0]
            to_split = split[1]
            out_of_sample_datetimes.append(
                ((date_from + timedelta(days=from_split * dt.days)).strftime("%d.%m.%Y"),
                 (date_from + timedelta(days=to_split * dt.days)).strftime("%d.%m.%Y"))
            )
        self.out_of_sample_datetimes = out_of_sample_datetimes
        return out_of_sample_datetimes