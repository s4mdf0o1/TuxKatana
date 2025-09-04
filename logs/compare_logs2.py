import argparse
from itertools import zip_longest
from termcolor import colored

# Séquences connues à mettre en évidence dans les DONNÉES (pas dans l'en-tête)
SEQUENCES_KNOWN = [
    ["F0", "41", "00", "00", "00", "00", "33"],  # exemple (mets ce que tu veux)
]

HEADER_PREFIX = ["[DEBUG]", "F0", "41", "00", "00", "00", "00", "33", "12"]

def to_tokens(line: str):
    """Découpe la ligne en tokens majuscules (pour éviter les faux négatifs f0 vs F0)."""
    return [t.upper() for t in line.strip().split()]

def hex_to_int(byte_list):
    return int("".join(byte_list), 16)

def trouver_positions_sequences(hex_list, sequences):
    """Retourne les positions (index) des octets inclus dans les séquences connues."""
    pos = set()
    for seq in sequences:
        L = len(seq)
        if L == 0:
            continue
        for i in range(len(hex_list) - L + 1):
            if hex_list[i:i+L] == seq:
                pos.update(range(i, i+L))
    return pos

def parse_line(tokens):
    """
    Extrait (adresse_de_base, data_tokens) d'une ligne.
    Si la ligne commence par l'en-tête attendu, on retire l'en-tête + 4 octets d'adresse.
    Sinon, on considère toute la ligne comme données, sans adresse.
    """
    if (len(tokens) >= 13 and
        tokens[0] == HEADER_PREFIX[0] and
        tokens[1:9] == HEADER_PREFIX[1:]):

        addr_start_bytes = tokens[9:13]  # 4 octets
        addr_start = hex_to_int(addr_start_bytes)
        data_tokens = tokens[13:]
        return addr_start, data_tokens
    else:
        return None, tokens  # pas d'adresse déduite

def comparer_logs(f1, f2):
    with open(f1, "r") as a, open(f2, "r") as b:
        lignes1 = a.readlines()
        lignes2 = b.readlines()

    differences = []  # (adresse, v1, v2)

    for lnum, (l1, l2) in enumerate(zip_longest(lignes1, lignes2, fillvalue=""), start=1):
        t1 = to_tokens(l1)
        t2 = to_tokens(l2)

        addr_start, data1 = parse_line(t1)
        _,          data2 = parse_line(t2)  # on aligne aussi le fichier 2 sur ses données

        L = max(len(data1), len(data2))
        data1 += ["--"] * (L - len(data1))
        data2 += ["--"] * (L - len(data2))

        # positions des séquences connues (sur data1 uniquement)
        seq_pos = trouver_positions_sequences(data1, SEQUENCES_KNOWN)

        out = []
        for i in range(L):
            v1, v2 = data1[i], data2[i]
            is_checksum = (i+1 < L and data1[i+1] == "F7")
            if v1 != v2 and not is_checksum:
                out.append(colored(f"[{v1}|{v2}]", "red", attrs=["bold"]))
                if addr_start is not None and v1 != "--":
                    differences.append((addr_start + i, v1, v2))
            elif i in seq_pos:
                out.append(colored(v1, "cyan", attrs=["bold"]))
            else:
                out.append(v1)

        print(" ".join(out))

    # Récapitulatif des différences avec adresses
    if differences:
        print("\n=== Différences trouvées ===")
        for addr, v1, v2 in differences:
            #print(f"Adresse 0x{addr:08X} : {v1} -> {v2}")
            addr_bytes = [(addr >> (8*i)) & 0xFF for i in reversed(range(4))]
            addr_str = " ".join(f"{b:02X}" for b in addr_bytes)
            print(f"Adresse {addr_str} : {v1} -> {v2}")
    else:
        print("\nAucune différence détectée.")

def main():
    parser = argparse.ArgumentParser(
        description="Compare deux fichiers hex (format DEBUG F0 41 ... 33 12 + 4 octets d'adresse) ; "
                    "affiche les différences sur les lignes et liste leurs adresses."
    )
    parser.add_argument("fichier1")
    parser.add_argument("fichier2")
    args = parser.parse_args()
    comparer_logs(args.fichier1, args.fichier2)

if __name__ == "__main__":
    main()

