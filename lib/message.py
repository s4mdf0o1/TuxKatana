from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from .tools import to_str, from_str

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class FormatMessage:
    def __init__( self ):
        with open("params/sysex.yaml", 'r') as f:
            raw = yaml.load(f)
        self.addrs = raw

        self.header = [int(v, 16) for v in "41 00 00 00 00 33".split(' ')]

    def get_from_name( self, cmd, name, value ):
        command = from_str(self.addrs[cmd])
        addr = from_str(self.addrs[name])
        data = addr + value
        cks = self.checksum(data)
        return self.header + command + data + cks

    def get_with_addr( self, cmd, addr, value ):
        command = from_str(self.addrs[cmd])
        data = addr + value
        cks = self.checksum(data)
        return self.header + command + data + cks


    def get_addr_data( self, msg ):
        msg = msg.hex()
        for t in ["F0 ", to_str(self.header)+" ", " F7"]:
            msg = msg.replace( t, "" )
        mlst = from_str(msg)
        cmd = mlst.pop(0)
        cks = mlst.pop(-1)
        if cks != self.checksum(mlst)[0]:
            raise ValueError(f"Checksum Error in {msg} ")
        return mlst[:4], mlst[4:]

    def get_str(self, msg):
        addr, data = self.get_addr_data(msg)
        return ''.join([chr(v) for v in data])

    def build(self, cmd, addr, data):
        cmd = self.addrs[cmd]
        cks = self.checksum( addr + data )
        msg = self.header + cmd + addr + data + cks
        return msg

    def decode(self, msg):
        log.debug(f"SysExMessage.decode({msg.hex()})")
        addr, data =  self.get_addr_data(msg)
        log.debug(f"{to_str(addr)}: {to_str(data)}")

    def decode_ident( self, data ):
        log.debug(f"decode_ident({[hex(i) for i in data]})")

    def checksum( self, data ):
        return [(128 - (sum(data) % 128)) % 128]
    

