
def to_str( d ):
    if isinstance(d, list):
        return " ".join(f"{i:02x}" for i in d).strip()
    elif isinstance(d, int):
        return f"{d:02x}"

def from_str( s: str):
    return [int(x, 16) for x in s.split()]

def bytes_to_int(data):
    if not isinstance(data, list):
        raise ValueError("param must be a list of int")
    value = 0
    for b in data:
        value = (value << 8) | b
    return value

#def hexstr_to_int(s):
#    """ Big Endian, space separated str chain to int"""
#    data = [int(x, 16) for x in s.split()]
#    return int.from_bytes(bytes(data), "big")

def int_to_midi_bytes(value, size=2):
    """int to N MIDI data bytes (7bits)."""
    data = []
    for _ in range(size):
        data.append(value & 0x7F)
        value >>= 7
    return list(reversed(data))

def midi_bytes_to_int(data):
    value = 0
    for i, b in enumerate(data):
        value |= (b & 0x7F) << (7 * i)
    return value

def midi_str_to_int(s: str) -> int:
    parts = s.split(' ')
    bytes_msb = [int(p, 16) & 0x7F for p in parts]
    value = 0
    for i, b in enumerate(reversed(bytes_msb)):
        value |= b << (7 * i)
    return value    
    data = [int(x, 16) for x in s.split()]
    value = 0
    for i, b in enumerate(data):
        value |= (b & 0x7F) << (7 * i)
    return value


