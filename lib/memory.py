from gi.repository import GLib, GObject, Gio

from lib.tools import to_str, from_str, midi_str_to_int, int_to_midi_bytes
from .address import Address

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
        self.Addr_start = mry_start #Address(mry_start)
        self.memory = []
        #self.loading = False
        self.base_addr = None
        self.map = {}

    def add_block(self, Addr_start, data):
        log.debug(f"{self.Addr_start} / {Addr_start}: {len(data)=}")
        if Addr_start == self.Addr_start:
            #self.loading = True
            self.memory = data #[]
            self.base_addr = Addr_start[:]
            return

        Addr_next = self.Addr_start + len(self.memory)

        if Addr_start > Addr_next:
            log.debug(f"{Addr_start} > {Addr_next}")
            diff = Addr_next - Addr_start
            log.debug(f"{len(self.memory)=}")
            self.memory.extend([0] * diff)
            log.debug(f"{diff=} -> {len(self.memory)=}")
            self.memory.extend(data)
            log.debug(f"{len(self.memory)=}")
            #self.emit("mry-loaded")
        elif Addr_start == Addr_next:
            # log.debug(f"{Addr_start} == {Addr_next}")
            self.memory.extend(data)
        else:
            raise ValueError(f"Mry calculation Error: {Addr_start=} {Addr_next=}")

    def read(self, Addr, size=1, dump = False):
        if not len(self.memory):
            raise RuntimeError("Empty Memory")
        offset = Addr - self.Addr_start
        value = self.memory[offset:offset+size]
        if len(value)==size and size==1:
            return value[0]
        elif dump:
            return to_str(value)
        else:
            return midi_str_to_int(to_str(value))

    def write(self, Addr, data):
        if not len(self.memory):
            raise RuntimeError("Empty Memory")
        if Addr == Address('00 01 00 00'):
            return
        offset = Addr - self.Addr_start #addr_to_offset(addr)
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
        mry_bytes=self.read(Address('60 00 00 00'), 16)
        preset_bytes = int_to_midi_bytes(mry_bytes, 16)
        # log.debug(f"{preset_bytes=}")
        preset_name= ''.join([chr(v) for v in preset_bytes])
        return preset_name

    # def addr_to_offset(self, addr):
    #     offset = 0
    #     mult = 1
    #     for a, b in zip(reversed(addr), reversed(self.mry_start)):
    #         offset += (a - b) * mult
    #         mult *= 128
    #     return offset

    # def offset_diff_addrs(self, addr_end, addr_start):
    #     offset = 0
    #     mult = 1
    #     for a, b in zip(reversed(addr_end), reversed(addr_start)):
    #         offset += (a - b) * mult
    #         mult *= 128
    #     return offset

    # def offset_to_addr(self, offset):
    #     b = self.mry_start[:]
    #     for i in range(len(b)-1, -1, -1):
    #         b[i] += offset % 128
    #         carry = b[i] // 128
    #         b[i] %= 128
    #         offset //= 128
    #         if carry and i > 0:
    #             b[i-1] += carry
    #     return b

    # def incr_base128(self, addr, n=1):
    #     b = addr[:]
    #     for _ in range(n):
    #         for i in range(len(b)-1, -1, -1):
    #             b[i] += 1
    #             if b[i] < 128:
    #                 break
    #             b[i] = 0
    #     return b


