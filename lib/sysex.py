from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

import logging
dbg = logging.getLogger("debug")
from lib.tools import to_str, from_str

class SysExMessage:
    def __init__( self ):
        dbg.debug("SysExMessage.__init__")
        with open("params/sysex.yaml", 'r') as f:
            raw = yaml.load(f)
        self.addrs = raw

        self.header = [int(v, 16) for v in "41 00 00 00 00 33".split(' ')]

    def build(self, cmd, addr, data):
        cmd = self.addrs[cmd]
        cks = self.checksum( addr + data )
        msg = self.header + cmd + addr + data + cks
        return msg

    def decode(self, msg):
        dbg.debug(f"SysExMessage.decode({msg.hex()})")
        addr, data =  self.get_addr_data(msg)
        dbg.debug(f"{to_str(addr)}: {to_str(data)}")

    def decode_ident( self, data ):
        dbg.debug(f"decode_ident({[hex(i) for i in data]})")

    def checksum( self, data ):
        return [(128 - (sum(data) % 128)) % 128]
    

