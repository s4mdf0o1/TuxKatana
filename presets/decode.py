#!/usr/bin/env python3
import json
import sys
import os
from ruamel.yaml import YAML
yaml = YAML(typ="rt")


# Vérification des arguments
if len(sys.argv) < 2:
    print("Usage: python script.py <fichier_entree.json>")
    sys.exit(1)

filein = sys.argv[1]
fileout = filein.split('.')[0] + "_read.tsl"

# Lecture du fichier JSON
with open(filein, "r", encoding="utf-8") as f:
    data = json.load(f)

yml = {}
#print(data['data'][0][0]['paramSet'])
for k, v in data['data'][0][0]['paramSet'].items():
    print(f"{k}: {len(v)=}\n{' '.join(v)}\n")
    yml[k] = len(v)
total = 0
for k, v in yml.items():
    print(k,v)
    total += v
print("total len:", total)

with open("format_preset.yaml", 'w') as f:
    yaml.dump(yml, f)
# Écriture du JSON formaté
#with open(fileout, "w", encoding="utf-8") as f:
#    json.dump(data, f, indent=4, ensure_ascii=False)

#print(f"✅ JSON formaté écrit dans {fileout}")

