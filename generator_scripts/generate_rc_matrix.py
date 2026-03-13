#!/usr/bin/env python3

import argparse

def sumbols_in_row(row, cols):
    symbols = 1
    if row >= 10:
        symbols += 1
    if cols >= 10:
        symbols += 1
    return symbols

def generate_rc_matrix(rows, cols, include_comments=True):
    key_num = 1
    max_symbols = sumbols_in_row(rows, cols)

    for row in range(rows):
        if include_comments:
            # Generate comment line with key labels
            keys = [f"{key_num + c}".center(max_symbols + 4 ) for c in range(cols)]
            print(f"//   {' | '.join(keys)}")
        
        # Generate RC line
        rcs = [f"RC({row},{col})".ljust(6+max_symbols) for col in range(cols)]
        print(f"    {' '.join(rcs)}")
        
        key_num += cols

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate RC matrix in ZMK style')
    parser.add_argument('--rows', type=int, default=3, help='Number of rows (default: 3)')
    parser.add_argument('--cols', type=int, default=3, help='Number of columns (default: 3)')
    parser.add_argument('--no-comments', action='store_true', help='Disable comment lines with key labels')
    
    args = parser.parse_args()
    generate_rc_matrix(args.rows, args.cols, include_comments=not args.no_comments)