
def to_str( d ):
    if isinstance(d, list):
        return " ".join(f"{i:02x}" for i in d).strip()
    elif isinstance(d, int):
        return f"{d:02x}"

def from_str( s: str):
    return [int(x, 16) for x in s.split()]


