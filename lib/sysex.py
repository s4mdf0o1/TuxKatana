from ruamel.yaml import YAML
#from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")
from collections import UserDict

import logging
dbg = logging.getLogger("debug")

class SysExML(UserDict):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        with open(filepath, 'r') as f:
            raw = yaml.load(f)
        self.data = raw

    def __getitem__(self, key):
        for k in self.data.keys():
            if key in self.data[k].keys():
                return self.from_str(self.data[k][key])

    def from_str(self, s: str):
        return [int(x, 16) for x in s.split()]

    def to_str( self, d):
        if isinstance(d, list):
            return " ".join(f"{i:02x}" for i in d)
        raise TypeError(f"Argument must be a list, got {type(d).__name__}")

    def save(self):
        dbg.debug(f"save: {self.data}")
        with open(self.filepath, 'w') as f:
            yaml.dump(self.data, f)

class SysExMessage:
    def __init__( self ):
        dbg.debug("SysExMessage.__init__")
        self.addrs = SysExML("params/sysex.yaml")
        self.header = [int(v, 16) for v in "41 00 00 00 00 33".split(' ')]

    def get_from_name( self, cmd, name, value ):
        command = self.addrs[cmd]
        addr = self.addrs[name]
        data = addr + value
        cks = self.checksum(data)
        return self.header + command + data + cks

    def get_with_addr( self, cmd, addr, value ):
        command = self.addrs[cmd]
        #addr = self.addrs[name]
        data = addr + value
        cks = self.checksum(data)
        return self.header + command + data + cks


    def get_addr_data( self, msg ):
        msg = msg.hex()
        for t in ["F0 ", self.addrs.to_str(self.header)+" ", " F7"]:
            msg = msg.replace( t, "" )
        mlst = self.addrs.from_str(msg)
        cmd = mlst.pop(0)
        cks = mlst.pop(-1)
        if cks != self.checksum(mlst)[0]:
            raise ValueError(f"Checksum Error in {msg} ")
        return mlst[:4], mlst[4:]

    def get_str(self, msg):
        addr, data = self.get_addr_data(msg)
        #dbg.debug(f"{data=}")
        return ''.join([chr(v) for v in data])

    def build(self, cmd, addr, data):
        cmd = self.addrs[cmd]
        cks = self.checksum( addr + data )
        msg = self.header + cmd + addr + data + cks
        return msg

    def decode(self, msg):
        dbg.debug(f"SysExMessage.decode({msg.hex()})")
        addr, data =  self.get_addr_data(msg)
        dbg.debug(f"{self.addrs.to_str(addr)}: {self.addrs.to_str(data)}")

    def decode_ident( self, data ):
        dbg.debug(f"decode_ident({[hex(i) for i in data]})")
        #print(app.katana)

    def checksum( self, data ):
        return [(128 - (sum(data) % 128)) % 128]
    

