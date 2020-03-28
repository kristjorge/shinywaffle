import os
import json
from datetime import datetime


class Reporter:

    def __init__(self, filename, path):
        self.path = path
        self.filename = filename

    def aggregate_report(self, data_dict):
        # Dump as json to file
        with open(self.path + "/" + self.filename + ".json", "w") as json_out:
            json.dump(data_dict, json_out, sort_keys=False, indent=3)
