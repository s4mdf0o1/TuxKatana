import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class MIDIBytes:
    def __init__(self, mb=None, length: int = None):
        if mb is None or mb == '':
            self.bytes = []
            return
        if isinstance(mb, int):
            if length is None:
                length = max(1, (mb.bit_length() + 6) // 7)
            mb = self.int_to_hexstring(mb, length)
        if isinstance(mb, list):
            mb = " ".join(f"{c:02X}" for c in mb).strip()
        parts = mb.strip().split()
        if not parts:
            self.bytes = []
            return
        try:
            vals = [int(p, 16) for p in parts]
        except ValueError:
            raise ValueError(f"Invalid Hex byte: {parts}")
        for v in vals:
            if v < 0 or v > 0x7F:
                raise ValueError(f"Invalid MIDI byte: 0 < {v} < 0x7F")
        if length and len(vals) < length:
            diff = length - len(vals)
            vals = [0]*diff + vals
            self.length = length
        self.bytes = vals

    def __str__(self):
        return " ".join(f"{b:02X}" for b in self.bytes)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.__str__()}')"

    def __eq__(self, other):
        if not isinstance(other, (Address,MIDIBytes,)):
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

    def __add__(self, other):
        if not isinstance(other, (int, MIDIBytes,)):
            return NotImplemented
        else:
            if isinstance(other, int):
                value = self.to_int() + other
                return MIDIBytes.from_int(value, len(self.bytes))
            else:
                return MIDIBytes(self.bytes + other.bytes)

    def __getitem__(self, i):
        return self.bytes[i]

    def __setitem__(self, i, value):
        if isinstance(i, slice):
            if isinstance(value, MIDIBytes):
                self.bytes[i] = value.bytes
            elif isinstance(value, list):
                self.bytes[i] = value
            else:
                raise TypeError("slice assignment requires list or MIDIBytes")
        else:
            if isinstance(value, int):
                if not (0 <= value <= 0x7F):
                    raise ValueError("MIDI byte must be in 0..127")
                self.bytes[i] = value
            else:
                raise TypeError("single item must be int")

    def __len__(self):
        return len(self.bytes)

    def __iter__(self):
        return iter(self.bytes)

    @property
    def int(self) -> int:
        return self.to_int()

    @property
    def bool(self) -> bool:
        if len(self.bytes) > 1:
            raise ValueError(f"Cannot convert multi-byte {self} to bool")
        if len(self.bytes) == 0:
            log.warning(f"midi_bytes.py:108- len(self.bytes) == 0")
            return False
        return self.bytes[0] != 0

    @property
    def str(self) -> str:
        return str(self)

    def to_gtype(self, val_type: str):
        # log.debug(f"{val_type=}")
        if val_type == 'gboolean':
            return self.bool
        elif val_type == 'gint':
            return self.int
        elif val_type == 'gchararray':
            return self.str
        elif val_type == 'gdouble':
            return float(self.int)
        else:
            log.warning(f"midi_bytes.py:127-Not recognized GType: {val_type}")
            return self

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
    def __init__(self, addr=None):
        if isinstance(addr, Address):
            log.debug(f"Double declaration of {addr}")
            return
        super().__init__(addr, length=4)

    def __add__(self, other):
        if not isinstance(other, (int, MIDIBytes,)):
            return NotImplemented
        if isinstance(other, int):
            value = self.to_int() + other
            return Address.from_int(value, len(self.bytes))
        if isinstance(other, MIDIBytes):
            return MIDIBytes(self.bytes + other.bytes)

    def __hash__(self):
        return self.int

    def __sub__(self, other):
        if isinstance(other, Address):
            val_s = self.to_int()
            val_o = other.to_int()
            return abs(val_s - val_o)
        elif isinstance(other, int):
            value = self.to_int() - other
            return Address.from_int(value, len(self.bytes))
        return NotImplemented


