import argparse
from itertools import zip_longest
from termcolor import colored

SEQUENCES_KNOWN = [["F0","41","00","00","00","00","33"],
                   "43 6C 65 61 6E 20 72 65 76 65 72 62 20 20 20 20".split(' ')]  # exemple

def to_tokens(line: str):
    return [t.upper() for t in line.strip().split()]

def parse_line(tokens):
    if len(tokens) >= 13 and tokens[0] == "[DEBUG]":
        addr_start = [int(x,16) for x in tokens[9:13]]
        data = tokens[13:]
        return addr_start, data
    return None, tokens

def incr_base128(addr, offset):
    b = addr[:]
    b[3] += offset
    for i in range(3,0,-1):
        if b[i] > 127:
            carry = b[i] // 128
            b[i] %= 128
            b[i-1] += carry
    return b

def fmt_addr(addr):
    return " ".join(f"{x:02X}" for x in addr)

def find_known_positions(data, seqs):
    pos = set()
    for seq in seqs:
        for i in range(len(data)-len(seq)+1):
            if data[i:i+len(seq)] == seq:
                pos.update(range(i,i+len(seq)))
    return pos

def comparer_logs(f1, f2):
    with open(f1) as a, open(f2) as b:
        lines1, lines2 = a.readlines(), b.readlines()

    differences = []

    for l1,l2 in zip_longest(lines1, lines2, fillvalue=""):
        t1, t2 = to_tokens(l1), to_tokens(l2)
        addr, data1 = parse_line(t1)
        _, data2 = parse_line(t2)

        if addr:
            print(f">>> {fmt_addr(addr)} > ", end="")
        else:
            print(">>>        > ", end="")

        L = max(len(data1), len(data2))
        data1 += ["--"]*(L-len(data1))
        data2 += ["--"]*(L-len(data2))

        seq_pos = find_known_positions(data1, SEQUENCES_KNOWN)
        out = []

        for i,(v1,v2) in enumerate(zip(data1,data2)):
            next_v1 = data1[i+1] if i+1 < L else None
            if v1 != v2:
                out.append(colored(f"[{v1}|{v2}]", "red", attrs=["bold"]))
                if addr and next_v1 != "F7" and v1 != "--":
                    diff_addr = incr_base128(addr,i)
                    differences.append((diff_addr,v1,v2))
            elif i in seq_pos:
                out.append(colored(v1,"cyan",attrs=["bold"]))
            else:
                out.append(v1)

        print(" ".join(out))

    if differences:
        print("\n=== Différences finales avec adresses exactes ===")
        for a,v1,v2 in differences:
            print(f"{fmt_addr(a)} : {v1} -> {v2}")
    else:
        print("\nAucune différence détectée.")

def main():
    parser = argparse.ArgumentParser(description="Compare deux fichiers hex et affiche les différences (base128).")
    parser.add_argument("fichier1")
    parser.add_argument("fichier2")
    args = parser.parse_args()
    comparer_logs(args.fichier1,args.fichier2)

if __name__=="__main__":
    main()

