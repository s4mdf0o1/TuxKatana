from collections import UserDict

from ruamel.yaml import YAML
yaml = YAML(typ="rt")

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class Map(UserDict):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        with open(filepath, 'r') as f:
            raw = yaml.load(f)
        self.data = raw
        self.recv = {}
        self.send = {}
        for param in self.data.values():
            if 'RECV' in param:
                self.recv[param['RECV']] = param['prop_name']
            if 'SEND' in param:
                self.send[param['prop_name']] = param['SEND']

    def save(self):
        with open(self.filepath, 'w') as f:
            yaml.dump(self.data, f)
        log.info(f"{self.filepath} saved")


