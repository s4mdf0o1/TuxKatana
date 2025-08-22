import mido

# Remplace par le port MIDI correct
KATANA_PORT = "KATANA:KATANA MIDI 1 28:0"
outport = mido.open_output(KATANA_PORT)

# Identifiant SysEx pour le Bass
param_id = 0x10

# Construction du message SysEx
sysex_msg = [0xF0, 0x41, 0x10, 0x42, 0x12, 0x00, param_id, 0xF7]
msg = mido.Message('sysex', data=sysex_msg)
outport.send(msg)

print(f"Requête SysEx envoyée pour récupérer la valeur de Bass (ID: {param_id:#04x})")

