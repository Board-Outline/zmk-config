#!/usr/bin/env python3

import argparse

def generate_kp_bindings(rows, cols):
    for row in range(rows):
        bindings = ["&kp N1  "] * cols
        print(' '.join(bindings))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate key bindings with &kp 1')
    parser.add_argument('--rows', type=int, default=3, help='Number of rows (default: 3)')
    parser.add_argument('--cols', type=int, default=3, help='Number of columns (default: 3)')
    
    args = parser.parse_args()
    generate_kp_bindings(args.rows, args.cols)