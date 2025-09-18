from .midi_bytes import MIDIBytes, Address

class SysEx:
    DEFAULT_HEADER = MIDIBytes('41 00 00 00 00 33').bytes

    def __init__(self, *args):
        if len(args) == 1 and hasattr(args[0], "type") and args[0].type == "sysex":
            # Parsing mido.Message('sysex')
            msg = args[0]
            self.header, self.command, self.address, self.data = self._parse_sysex(msg)
        elif len(args) == 3:
            # Prepare mido message
            self.command, self.address, self.data = args
            self.header = self.DEFAULT_HEADER
        else:
            raise ValueError("Invalid SysEx constructor usage")

        self.checksum = self._compute_checksum(self.address.bytes + self.data.bytes)

    def _compute_checksum(self, data: list[int]) -> list[int]:
        return [(128 - (sum(data) % 128)) % 128]

    def _parse_sysex(self, msg):
        raw = msg.data
        # extract header
        header_size = len(self.DEFAULT_HEADER)
        header = raw[:header_size]
        body = raw[header_size:]
        if len(body) < 5:
            raise ValueError("Message too short")

        command = MIDIBytes(body[0])
        address = Address(" ".join(f"{b:02x}" for b in body[1:5]))
        data = MIDIBytes(" ".join(f"{b:02x}" for b in body[5:]))
        return header, command, address, data

    def get_addr_data(self):
        return self.address.bytes, self.data.bytes

    def get_mido_message(self):
        from mido import Message
        body = self.command.bytes + self.address.bytes + self.data.bytes + self.checksum
        return Message('sysex', data=self.header + body)

    def __repr__(self):
        return f"<SysEx cmd={self.command} addr={self.address} data={self.data}>"

    def __str__(self):
        full_list = [0xF0]+self.header+self.command.bytes+self.address.bytes+self.data.bytes+self.checksum+[0xF7]
        return ' '.join(f"{b:02x}" for b in full_list)

class SysExFactory:
    def __init__(self, yaml_path="params/sysex.yaml"):
        with open(yaml_path, 'r') as f:
            raw = yaml.load(f, Loader=yaml.FullLoader)
        self.addrs = {}
        for k, v in raw.items():
            #if '0X' in v:
            #    self.addrs[k] = MIDIBytes(int(v, 16))
            #else:
            self.addrs[k] = Address(v)

    def create(self, cmd_name: str, addr_name: str, value: list[int] | MIDIBytes) -> SysEx:
        command = self.addrs[cmd_name]  if isinstance(self.addrs[cmd_name], MIDIBytes) \
                                            else MIDIBytes(self.addrs[cmd_name])
        address = self.addrs[addr_name] if isinstance(self.addrs[addr_name], Address) \
                                            else Address(self.addrs[addr_name])
        if isinstance(value, list):
            data = MIDIBytes(' '.join(f"{v:02X}" for v in value))
        else:
            data = value
        return SysEx(command, address, data)

