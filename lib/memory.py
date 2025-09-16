from gi.repository import GLib, GObject, Gio

from lib.tools import to_str, from_str, midi_str_to_int, int_to_midi_bytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class Memory(GObject.GObject):
    __gsignals__ = {
        "mry-loaded": (GObject.SignalFlags.RUN_FIRST, None, ()),
        #"channel-changed": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }
    def __init__(self, mry_start):
        super().__init__()
        self.mry_start = mry_start
        self.memory = []
        #self.loading = False
        self.base_addr = None
        self.map = {}

    def add_block(self, addr_start, data):
        log.debug(f"{to_str(addr_start)}: {len(data)=}")
        if addr_start == self.mry_start:
                    #from_str(self.sysex.addrs['MEMORY']):
            #self.loading = True
            self.memory = []
            self.base_addr = addr_start[:]
            
        if not self.memory:
            self.base_addr = addr_start[:]
            self.memory.extend(data)
            return
        log.debug(f"{to_str(self.base_addr)}: {len(data)=}")
        addr_next = self.incr_base128(self.base_addr, len(self.memory))
        if self.base_addr != addr_next:
            #log.debug("mry-changed")
            diff = self.offset_diff_addrs(addr_next, addr_start)
            self.memory.extend([0] * diff)
            log.debug(f"{to_str(self.base_addr)} >= {to_str(addr_next)}")
            #self.emit("mry-loaded")
            #self.loading = False
            #expn = to_str(expected_next)
            #adst = to_str(addr_start)
        else:
            self.memory.extend(data)

    def read_from_str(self, saddr, size=1):
        #log.debug(f"{to_str(self.offset_to_addr(len(self.memory)-1))}")
        # log.debug(f"'{saddr}': {size=}, {len(self.memory)=}")
        return self.read(from_str(saddr), size)
    def read(self, addr, size=1):
        if not self.base_addr:
            raise RuntimeError("Empty Memory")
        offset = self.addr_to_offset(addr)
        value = self.memory[offset:offset+size]
        if len(value)==size and size==1:
            return value[0]
        else:
            return midi_str_to_int(to_str(value))

    def write_from_str(self, saddr, data):
        log.debug(f"{saddr} {to_str(data)}")
        self.write( from_str(saddr), data)
    def write(self, addr, data):
        if not self.base_addr:
            raise RuntimeError("Empty Memory")
        offset = self.addr_to_offset(addr)
        if isinstance(data, int):
            data = [data]
        if offset + len(data) > len(self.memory):
            raise IndexError("Write exceeds memory size")
        self.memory[offset:offset + len(data)] = data

    def save_to_file(self, filename="memory_dump.bin"):
        with open(filename, "wb") as f:
            f.write(bytes(self.memory))
        log.info(f"✅ Memory saved to {filename}")

    def get_preset_name(self):
        mry_bytes=self.read_from_str('60 00 00 00', 16)
        preset_bytes = int_to_midi_bytes(mry_bytes, 16)
        # log.debug(f"{preset_bytes=}")
        preset_name= ''.join([chr(v) for v in preset_bytes])
        return preset_name

    def get_block(self, saddr, size):
        #log.debug(f"{saddr}, {size=}")
        return self.read_from_str(saddr, size)
        
    def addr_to_offset(self, addr):
        offset = 0
        mult = 1
        for a, b in zip(reversed(addr), reversed(self.mry_start)):
            offset += (a - b) * mult
            mult *= 128
        return offset

    def offset_diff_addrs(self, addr_end, addr_start):
        offset = 0
        mult = 1
        for a, b in zip(reversed(addr_end), reversed(addr_start)):
            offset += (a - b) * mult
            mult *= 128
        return offset

    def offset_to_addr(self, offset):
        b = self.mry_start[:]
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


