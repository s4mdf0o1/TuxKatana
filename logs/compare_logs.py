#!/usr/bin/env python3
import argparse
from termcolor import colored

# Séquences connues à surligner
SEQUENCES_KNOWN = [
    ["F0", "41", "00", "00", "00", "00", "33"],
    ["60", "00"],
    "43 6C 65 61 6E 20 72 65 76 65 72 62 20 20 20 20".split(' ')
]

def trouver_positions_sequences(hex_list, sequences):
    """Retourne un set des positions des séquences connues."""
    positions = set()
    for seq in sequences:
        seq_len = len(seq)
        for i in range(len(hex_list) - seq_len + 1):
            if hex_list[i:i+seq_len] == seq:
                positions.update(range(i, i+seq_len))
    return positions

def comparer_logs(f1, f2):
    with open(f1, "r") as f:
        lignes1 = f.readlines()
    with open(f2, "r") as f:
        data2 = f.read().split()

    index_global = 0  # pour suivre la position dans data2
    for ligne in lignes1:
        hex_list1 = ligne.strip().split()
        longueur = len(hex_list1)
        hex_list2 = data2[index_global:index_global+longueur]
        if len(hex_list2) < longueur:
            hex_list2 += ["--"] * (longueur - len(hex_list2))

        # Repérer les positions des séquences connues
        seq_positions = trouver_positions_sequences(hex_list1, SEQUENCES_KNOWN)

        ligne_resultat = []
        for i in range(longueur):
            val1, val2 = hex_list1[i], hex_list2[i]

            if val1 != val2:
                ligne_resultat.append(colored(f"[{val1}|{val2}]", 'red', attrs=['bold']))
            elif i in seq_positions:
                ligne_resultat.append(colored(val1, 'cyan', attrs=['bold']))
            else:
                ligne_resultat.append(val1)

        print(" ".join(ligne_resultat))
        index_global += longueur

def main():
    parser = argparse.ArgumentParser(description="Comparer deux fichiers hex et mettre en évidence les différences et séquences connues en respectant les retours à la ligne")
    parser.add_argument("fichier1", help="Chemin du premier fichier hex")
    parser.add_argument("fichier2", help="Chemin du second fichier hex")
    args = parser.parse_args()

    comparer_logs(args.fichier1, args.fichier2)

if __name__ == "__main__":
    main()

