#!/usr/bin/env python3
import json
import sys
import os

# Vérification des arguments
if len(sys.argv) < 2:
    print("Usage: python script.py <fichier_entree.json>")
    sys.exit(1)

filein = sys.argv[1]
fileout = filein.split('.')[0] + "_read.tsl"

# Lecture du fichier JSON
with open(filein, "r", encoding="utf-8") as f:
    data = json.load(f)

# Écriture du JSON formaté
with open(fileout, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ JSON formaté écrit dans {fileout}")

