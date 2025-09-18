from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from .tools import to_str, from_str
from .midi_bytes import Address, MIDIBytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class FormatMessage:
    def __init__( self ):
        with open("params/sysex.yaml", 'r') as f:
            raw = yaml.load(f)
        self.addrs = raw
        for k, v in self.addrs.items():
            if not '0X' in v:
                self.addrs[k] = Address(v)
            else:
                self.addrs[k] = v

        self.header = [int(v, 16) for v in "41 00 00 00 00 33".split(' ')]

    def get_from_name( self, cmd, name, value ):
        command = self.addrs[cmd].bytes
        baddr = self.addrs[name].bytes
        data = baddr + value
        cks = self.checksum(data)
        return self.header + command + data + cks

    def get_with_addr( self, cmd, Addr, value ):
        command = self.addrs[cmd].bytes
        data = Addr.bytes + value
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

    def checksum( self, data ):
        return [(128 - (sum(data) % 128)) % 128]
    

