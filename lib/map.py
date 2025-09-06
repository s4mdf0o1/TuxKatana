from collections import UserDict

from ruamel.yaml import YAML
#from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import logging
dbg = logging.getLogger("debug")

class Map(UserDict):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        with open(filepath, 'r') as f:
            raw = yaml.load(f)
        self.data = raw
        self.recv = []
        self.send = {}
        for param in self.data.values():
            if 'RECV' in param:
                #dbg.debug((param['RECV'], param['prop_name']))
                self.recv.append((param['RECV'], param['prop_name']))
            if 'SEND' in param:
                self.send[param['prop_name']] = param['SEND']
        #dbg.debug(f"{self.recv=}")
        #dbg.debug(f"{self.send=}")

    def save(self):
        with open(self.filepath, 'w') as f:
            yaml.dump(self.data, f)
        dbg.info(f"{self.filepath} saved")


