import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class MIDIBytes:
    def __init__(self, mb, length: int = None):
        log.debug(f"{mb=}")
        if mb is None or mb == '':
            self.bytes = []
            return
        if isinstance(mb, int):
            if length is None:
                length = max(1, (mb.bit_length() + 6) // 7)
            mb = self.int_to_hexstring(mb, length)
        if isinstance(mb, list):
            mb = " ".join(f"{c:02x}" for c in mb).strip()
        parts = mb.strip().split()
        if not parts:
            self.bytes = []
            return
            raise ValueError("Empty value")
        try:
            vals = [int(p, 16) for p in parts]
        except ValueError:
            raise ValueError(f"Invalid Hex byte: {parts}")
        for v in vals:
            if v < 0 or v > 0x7F:
                raise ValueError(f"Invalid MIDI byte: 0 < {v} < 0x7F")
        self.bytes = vals

    def __str__(self):
        return " ".join(f"{b:02x}" for b in self.bytes)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.__str__()}')"

    def __eq__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return self.bytes == other.bytes

    def __lt__(self, other):
        if not isinstance(other, MIDIBytes):
            return NotImplemented
        return self.to_int() < other.to_int()

    def __le__(self, other):
        if not isinstance(other, MIDIBytes):
            return NotImplemented
        return self.to_int() <= other.to_int()

    def __gt__(self, other):
        if not isinstance(other, MIDIBytes):
            return NotImplemented
        return self.to_int() > other.to_int()

    def __ge__(self, other):
        if not isinstance(other, MIDIBytes):
            return NotImplemented
        return self.to_int() >= other.to_int()

    def __add__(self, offset: int):
        if not isinstance(offset, int):
            return NotImplemented
        value = self.to_int() + offset
        return MIDIBytes.from_int(value, len(self.bytes))

    def __sub__(self, other):
        if isinstance(other, MIDIBytes):
            return abs(self.to_int() - other.to_int())
        elif isinstance(other, int):
            value = self.to_int() - other
            return MIDIBytes.from_int(value, len(self.bytes))
        return NotImplemented

    def __getitem__(self, i):
        return self.bytes[i]

    def to_int(self) -> int:
        value = 0
        n = len(self.bytes)
        for i, b in enumerate(self.bytes):
            shift = 7 * (n - 1 - i)
            value |= (b & 0x7F) << shift
        return value

    def to_chars(self) -> str:
        chars = ''.join(chr(b) for b in self.bytes)
        return chars

    @staticmethod
    def int_to_hexstring(value: int, length: int) -> str:
        if not isinstance(value, int):
            raise TypeError("value must be int")
        if value < 0:
            raise ValueError("value must be >= 0")
        maxval = 1 << (7 * length)
        if value >= maxval:
            raise OverflowError(f"value {value} not containing in {length} 7bits bytes")

        parts = []
        for i in range(length):
            shift = 7 * (length - 1 - i)
            parts.append((value >> shift) & 0x7F)
        return " ".join(f"{b:02X}" for b in parts)

    @classmethod
    def from_int(cls, value: int, length: int = None):
        if length is None:
            length = max(1, (value.bit_length() + 6) // 7)
        return cls(cls.int_to_hexstring(value, length))

class Address(MIDIBytes):
    def __init__(self, addr):
        super().__init__(addr, length=4)


