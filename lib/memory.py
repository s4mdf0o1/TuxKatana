from gi.repository import GLib, GObject, Gio

from .midi_bytes import Address, MIDIBytes

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
        self._timer_id = None
        self.Addr_start = mry_start
        self.memory = MIDIBytes()
        self.loading = False
        self.base_addr = Address()
        self.map = {}

    def _on_timeout(self):
        self._timer_id = None
        self.emit("mry-loaded")
        return False

    def add_block(self, Addr_start, data):
        # log.debug(f"{self.Addr_start} / {Addr_start}: {len(data.bytes)} {self.Addr_start+len(self.memory)}")
        if self._timer_id:
            GLib.source_remove(self._timer_id)
        self._timer_id = GLib.timeout_add(500, self._on_timeout)

        if Addr_start == self.Addr_start:

            self.loading = True
            self.memory += data
            self.base_addr = Addr_start[:]
            return

        Addr_next = self.Addr_start + len(self.memory)

        if Addr_start > Addr_next:
            diff = Addr_next - Addr_start
            self.memory += MIDIBytes('00', diff)
            # log.debug(f"{diff=} -> {len(self.memory)=}")
            self.memory += data
            # log.debug(f"{len(self.memory)=}")
        elif Addr_start == Addr_next:
            self.memory += data
        else:
            raise ValueError(f"Mry calculation Error: {Addr_start=} {Addr_next=}")

    def read(self, Addr, size=1, dump = False):
        if not len(self.memory):
            raise RuntimeError("Empty Memory")
        offset = Addr - self.Addr_start
        data = self.memory[offset:offset+size]
        return MIDIBytes(data)

    def write(self, Addr, data):
        # log.debug(f"{Addr} {data}")
        if not len(self.memory):
            raise RuntimeError("Empty Memory")
        if Addr == Address('00 01 00 00'):
            return
        offset = Addr - self.Addr_start
        size = offset + len(data)
        if size > len(self.memory):
            raise IndexError("Write exceeds memory size")

        self.memory[offset:size] = data.bytes

    def save_to_file(self, filename="memory_dump.bin"):
        with open(filename, "wb") as f:
            f.write(bytes(self.memory))
        log.info(f"✅ Memory saved to {filename}")

    def get_actual_preset(self):
        mry_bytes=self.read(Address('60 00 00 00'), 16)
        return mry_bytes.to_chars()


