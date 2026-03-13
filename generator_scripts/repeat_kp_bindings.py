#!/usr/bin/env python3

import argparse


def generate_kp_bindings(rows, cols):
    # sequence: N0 to N9 then letters A-Z, looping
    seq = [f"N{i}" for i in range(10)] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    total = rows * cols
    bindings = []
    for i in range(total):
        val = seq[i % len(seq)]
        bindings.append(f"&kp {val:<2}  ")

    # print row by row
    for r in range(rows):
        start = r * cols
        end = start + cols
        print(' '.join(bindings[start:end]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate key bindings with repeating &kp values (N0 to N9 then a-z)')
    parser.add_argument('--rows', type=int, default=3, help='Number of rows (default: 3)')
    parser.add_argument('--cols', type=int, default=3, help='Number of columns (default: 3)')
    args = parser.parse_args()
    generate_kp_bindings(args.rows, args.cols)
