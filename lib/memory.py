from gi.repository import GLib, GObject, Gio

from lib.tools import to_str, from_str

import logging
dbg = logging.getLogger("debug")
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)

class Memory(GObject.GObject):
    __gsignals__ = {
        "mry-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    def __init__(self, sysex):
        super().__init__()
        self.sysex = sysex
        self.memory = []
        self.loading = False
        self.base_addr = None
        self.map = {}

    def add_block(self, addr_start, data):
        dbg.debug(f"{len(data)=}")
        if addr_start == from_str(self.sysex.addrs['MEMORY']):
            self.loading = True
            self.memory = []
            self.base_addr = addr_start[:]

        if not self.memory:
            self.base_addr = addr_start[:]
            self.memory.extend(data)
            return
        expected_next = self.incr_base128(self.base_addr, len(self.memory))
        if addr_start != expected_next:
            self.emit("mry-changed")
            self.loading = False
            expn = to_str(expected_next)
            adst = to_str(addr_start)
            dbg.warn(f"Unintended Block: {expn=}, recvd: {adst=}, skipped: {len(data)}")
        else:
            self.memory.extend(data)

    def read_from_str(self, saddr, size=1):
        addr = [int(v, 16) for v in saddr.split(' ')]
        return self.read(addr, size)

    def read(self, addr, size=1):
        if not self.base_addr:
            raise RuntimeError("Empty Memory")
        offset = self.addr_to_offset(addr)
        value = self.memory[offset:offset+size]
        if len(value)==size and size==1:
            value = value[0]
        else:
            value=None
        return value

    def received_msg(self, msg):
        log_sysex.debug(f"{msg.hex()}")
        addr, data =  self.sysex.get_addr_data(msg)
        if len(data) > 63:
            self.add_block(addr, data)
        else:
            saddr = to_str(addr)
            sdata = to_str(data)
            dbg.debug(f"{saddr=}: {sdata=}")
            if saddr in self.map:
                mapping = self.map[saddr]
                if saddr == "60 00 06 50":
                    dbg.debug("CHANGE AMP")
                obj = mapping["obj"]
                prop = mapping["prop"]
                obj.handler_block(obj.handler_id)
                if isinstance(getattr(obj, prop), bool):
                    setattr(obj, prop, bool(data[0]))
                else:
                    setattr(obj, prop, int(data[0]))
                obj.handler_unblock(obj.handler_id)


    def addr_to_offset(self, addr):
        offset = 0
        mult = 1
        for a, b in zip(reversed(addr), reversed(self.base_addr)):
            offset += (a - b) * mult
            mult *= 128
        return offset

    def offset_to_addr(self, offset):
        b = self.base_addr[:]
        for i in range(len(b)-1, -1, -1):
            b[i] += offset % 128
            carry = b[i] // 128
            b[i] %= 128
            offset //= 128
            if carry and i > 0:
                b[i-1] += carry
        return b

    def incr_base128(self, addr, n=1):
        b = addr[:]
        for _ in range(n):
            for i in range(len(b)-1, -1, -1):
                b[i] += 1
                if b[i] < 128:
                    break
                b[i] = 0
        return b


