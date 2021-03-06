"""
Generate argument list for benchmark Gradien Boost
"""

from sklearn.model_selection import ParameterGrid
from util import write_config_file
import argparse

parser = argparse.ArgumentParser(description="Generate configuration file for bench_gb")
parser.add_argument('tool', help="configuration for which tool", choices=['time', 'perf', 'pin'])
args = parser.parse_args()

if args.tool == 'pin':
    arg_dict = {
        "--loss": ['deviance', 'exponential'],
        "--presort": [True, False],
        "-ns": [100, 400, 1600],
        "-nf": [10, 40, 160]
    }
elif args.tool == 'time' or args.tool == 'perf':
    arg_dict = {
        "--loss": ['deviance', 'exponential'],
        "--presort": [True, False],
        "-ns": [10000, 100000, 1000000],
        "-nf": [100, 1000, 10000]
    }

arg_grid = ParameterGrid(arg_dict)

config_filename = 'bench_gb.{}cfg'.format(args.tool)

write_config_file(config_filename, arg_grid)
