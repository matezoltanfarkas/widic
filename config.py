# use ~/widic.yaml as config file
import os
from enum import StrEnum

from ruamel.yaml import YAML

import telemetry


class Keys(StrEnum):
    DEFAULT_LANGUAGE = "default_language"
    USER_ID = "userid"


yaml = YAML(typ="rt")


class ConfigHandler:
    if not os.path.exists(os.path.expanduser("~/.config")):
        os.makedirs(os.path.expanduser("~/.config"))
    config_file = os.path.expanduser("~/.config/widic.yaml")

    def __init__(self):
        if not os.path.exists(self.config_file):
            self.config_data = yaml.load(f"{Keys.DEFAULT_LANGUAGE}: en\n{Keys.USER_ID}: 0 # Used for telemetry\n")
            self.config_data[Keys.DEFAULT_LANGUAGE] = "en"
            yaml.dump(self.config_data, open(self.config_file, "w+"))

        self.config_data = yaml.load(open(self.config_file, "r"))

    def set(self, key, value):
        self.config_data[key] = value
        yaml.dump(self.config_data, open(self.config_file, "w+"))

    def get(self, key):
        return self.config_data[key]

    def __getitem__(self, key):
        return self.config_data[key]
