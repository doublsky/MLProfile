"""
Generate argument list for benchmark linear regression.
"""

from sklearn.model_selection import ParameterGrid
from util import write_config_file
import argparse

parser = argparse.ArgumentParser(description="Generate configuration file for bench_linear")
parser.add_argument('tool', help="configuration for which tool", choices=['time', 'perf', 'pin'])
args = parser.parse_args()

if args.tool == 'pin':
	config_dict = {
		'--fit_intercept': [True, False],
		'--normalize': [False, True],
	    '-ns': [100, 200, 400, 800],
	    '-nf': [10, 20, 40, 80]
	}
elif args.tool == 'time' or args.tool == 'perf':
	config_dict = {
		'--fit_intercept': [True, False],
		'--normalize': [False, True],
	    '-ns': [10000, 100000, 1000000],
	    '-nf': [100, 1000, 10000]
	}

config_grid = ParameterGrid(config_dict)

config_filename = 'bench_linear.{}cfg'.format(args.tool)

write_config_file(config_filename, config_grid)
