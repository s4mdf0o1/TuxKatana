from .midi_bytes import MIDIBytes, Address

import mido
from mido.messages.messages import SysexData

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class SysEx(MIDIBytes):
    GET = MIDIBytes('11')
    SET = MIDIBytes('12')

    def __init__(self, body=None):
        self.mido = mido.Message('sysex')
        self.received = False
        if not body:
            return
        super().__init__(body)

    def recvd(self, msg):
        self.received = True
        if isinstance(msg, SysexData):
            msg = MIDIBytes(list(msg))
        if msg[:4] == MIDIBytes('7E 00 06 02').bytes: # Recv infos -> Header
            self.header = self._set_header(msg.bytes)
            return self

        self.addr, self.data, self.checksum = self._get_addr_data(msg.bytes)
        return self

    def get(self, addr, data=None, SET=False):
        self.received = False
        baddr = addr
        bdata = data
        if not isinstance(addr, Address):
            baddr = Address(addr)
        if not isinstance(data, MIDIBytes):
            bdata = MIDIBytes(data)
        command = self.GET if not SET else self.SET
        if str(baddr) == '7E 00 06 01': # Request device infos: Address+no data
            self.mido.data = baddr
            return self.mido
        msg = self.header
        checksum = self._checksum(baddr + bdata)
        self.mido.data = self.header + command + baddr + bdata + checksum
        self.command = command
        self.addr = baddr
        self.data = bdata
        self.checksum = checksum
        return  self.mido

    def values(self):
        return (self.addr, self.data)

    def copy(self):
        new = SysEx()
        if hasattr(self, "header"):
            new.header = MIDIBytes(self.header.bytes[:])
        if hasattr(self, "addr"):
            new.addr = Address(self.addr.bytes[:])
        if hasattr(self, "data"):
            new.data = MIDIBytes(self.data.bytes[:])
        return new

    def __str__(self):
        if hasattr(self, "addr"):
            saddr = " ".join(f"{b:02X}" for b in self.addr)
            saddr = '\033[33m' + saddr + '\033[0m'
            sg = '\033[32m>▷▶\033[0m' if self.received \
                    else '\033[31m<◁◀\033[0m'
            if hasattr(self, "data"):
                sdata = " ".join(f"{b:02X}" for b in self.data)
                sdata = '\033[36m' + sdata + '\033[0m'
                rec = "\033[32m▶\033[0m" if self.received \
                        else "\033[31m◀\033[0m"
                return f"{sg}[{saddr}]{rec} _{sdata}_ ({len(self.data)})"
        elif hasattr(self, "header"):
            s_head = " ".join(f"{b:02X}" for b in self.header.bytes)
            return f"<{s_head}>"
        return "Empty SysEx"


    def to_chars(self) -> str:
        chars = ''.join(chr(b) for b in self.data)
        return chars.strip()

    def _get_addr_data(self, body):
        body=list(body)
        checksum = body.pop(-1)
        if body[:len(self.header)] == self.header.bytes:
            body = body[len(self.header):]
        command = body.pop(0)
        return Address(body[:4]), MIDIBytes(body[4:]), checksum

    def _checksum(self, body):
        return MIDIBytes([(128 - (sum(body) % 128)) % 128])


    def _set_header(self, body):
        checksum = body.pop(-1)
        addr, data = body[:4], body[4:]
        manufacturer = [data[0]]
        device = [0]
        model = [0,0,0, data[1]]
        version = data[2]
        return MIDIBytes(manufacturer) + MIDIBytes(device) + MIDIBytes(model)

