from collections import UserDict
from bidict import bidict

from ruamel.yaml import YAML
yaml = YAML(typ="rt")

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str

class Map(UserDict):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        data = None
        self.recv = {}
        self.send = {}
        with open(filepath, 'r') as f:
            data = yaml.load(f)
        #self.data = raw
        for k in data:
            if k == 'SEND':
                self.send = bidict(data[k])
            elif k == 'RECV':
                self.recv = bidict(data[k])
            else:
                self.data[k] = bidict(data[k])
        self.recv |= self.send.inverse

    def get_addr(self, prop):
        addr=None
        if prop in self.recv.values():
            addr = from_str(self.recv.inverse[prop])
        elif prop in self.send:
            addr = from_str(self.send[prop])
        if not addr:
            log.warning(f"No Address for {prop}")
        return addr


            
    def save(self):
        with open(self.filepath, 'w') as f:
            yaml.dump(self.data, f)
        log.info(f"{self.filepath} saved")


