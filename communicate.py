import mido
import time

# -----------------------------
# Configuration port MIDI
# -----------------------------
KATANA_PORT = "KATANA:KATANA MIDI 1 28:0"  # Remplace selon get_output_names()
outport = mido.open_output(KATANA_PORT)
inport  = mido.open_input(KATANA_PORT)

# -----------------------------
# Fonction pour envoyer SysEx
# -----------------------------
def request_parameter(param_id):
    """
    Envoie une requête SysEx pour lire un paramètre Katana.
    param_id : identifiant du paramètre (0..127)
    """
    # Seuls les octets de données (<=127) doivent être inclus dans data
    sysex_data = [0x41, 0x10, 0x42, 0x12, 0x00, param_id]
    msg = mido.Message('sysex', data=sysex_data)
    outport.send(msg)
    print(f"Requête SysEx envoyée pour param ID={param_id:#04x}")

# -----------------------------
# Fonction pour lire réponses
# -----------------------------
def read_responses(timeout=1.0):
    """
    Lit tous les messages entrants pendant timeout secondes et les affiche.
    """
    start = time.time()
    while time.time() - start < timeout:
        for msg in inport.iter_pending():
            print("Reçu:", msg)

# -----------------------------
# Paramètres Katana 100 et leurs IDs
# -----------------------------
parameters = {
    "Canal": 0x00,
    "Gain": 0x01,
    "Volume": 0x02,
    "Master Volume": 0x1B,
    "Bass": 0x10,
    "Mid": 0x11,
    "Treble": 0x12,
    "Presence": 0x13,
    "Reverb": 0x14,
    "Delay": 0x15,
    "Chorus": 0x16,
    "Boost": 0x17,
    "Modulation": 0x18,
    "FX Loop": 0x19,
    "Tone Setting": 0x1A,
    "Pedal FX": 0x1C,
    "Expression Pedal": 0x1D
}

# -----------------------------
# Boucle pour interroger tous les paramètres
# -----------------------------
for name, pid in parameters.items():
    request_parameter(pid)
    time.sleep(0.1)  # Pause pour laisser le Katana répondre
    read_responses()

