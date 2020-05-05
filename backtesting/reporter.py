import json


class Reporter:

    def __init__(self, filename: str, path: str):
        self.path = path
        self.filename = filename

    def aggregate_report(self, data_dict: dict):
        with open(self.path + "/" + self.filename + ".json", "w") as json_out:
            json.dump(data_dict, json_out, sort_keys=False, indent=3)


class Reportable:

    def __init__(self):
        pass

    def report(self):
        attributes = [a for a in dir(self) if not a.startswith("__")
                      and not a.startswith("_")
                      and a not in dir("__builtins__")
                      and not hasattr(getattr(self, a), "__call__")]

        data = {}
        incr_data = {}
        for a in attributes:
            try:
                incr_data[a] = getattr(self, a).report()
            except AttributeError:
                incr_data[a] = getattr(self, a)

        data.update(incr_data)
        return data


