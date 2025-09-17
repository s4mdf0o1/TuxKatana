class Address:
    def __init__(self, s: str):
        if isinstance(s, list):
            s = " ".join(f"{c:02x}" for c in s).strip()
        parts = s.strip().split()
        if not parts:
            raise ValueError("Empty address")
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
        return f"Address('{self.__str__()}')"

    def __eq__(self, other):
        return self.bytes == other.bytes

    def __lt__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return self.to_int() < other.to_int()

    def __le__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return self.to_int() <= other.to_int()

    def __gt__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return self.to_int() > other.to_int()

    def __ge__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return self.to_int() >= other.to_int()

    def __add__(self, offset: int):
        if not isinstance(offset, int):
            return NotImplemented
        value = self.to_int() + offset
        return Address.from_int(value, len(self.bytes))

    def __sub__(self, other):
        if isinstance(other, Address):
            return abs(self.to_int() - other.to_int())
        elif isinstance(other, int):
            value = self.to_int() - other
            return Address.from_int(value, len(self.bytes))
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

    @classmethod
    def from_int(cls, value: int, length: int):
        if not isinstance(value, int):
            raise TypeError("value must be int")
        if value < 0:
            raise ValueError("value must be >= 0")
        maxval = 1 << (7 * length)
        if value >= maxval:
            raise OverflowError(f"value {value} ne tient pas dans {length} octets 7 bits")
        parts = []
        for i in range(length):
            shift = 7 * (length - 1 - i)
            parts.append((value >> shift) & 0x7F)
        return cls(" ".join(f"{b:02X}" for b in parts))


