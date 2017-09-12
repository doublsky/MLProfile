"""
Parse .args file to .csv file.
"""

import argparse
import pandas as pd
import re

parser = argparse.ArgumentParser(description='Parse .args files to .csv files.')
parser.add_argument('argfile', type=str,
                    help='Path to input .args file')
parser.add_argument('csvfile', type=str,
                    help='Path to output .csv file')

args = parser.parse_args()

result = pd.DataFrame()
idx = 0

with open(args.argfile, 'r') as argf:
    for line in argf:
        argslist = line.split()
        for key, value in zip(argslist[0::2], argslist[1::2]):
            result.set_value(idx, re.sub('^-+', '', key), value)
        idx += 1

result.to_csv(args.csvfile, index=False)
