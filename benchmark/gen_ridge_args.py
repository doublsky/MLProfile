"""
Generate argument list for benchmark ridge regression.
"""

from sklearn.model_selection import ParameterGrid
from util import write_config_file
import argparse

parser = argparse.ArgumentParser(description="Generate configuration file for bench_ridge")
parser.add_argument("tool", help="configuration for which tool", choices=["time", "perf", "pin"])
args = parser.parse_args()

if args.tool == "pin":
    arg_dict = {
        "--fit_intercept": [True, False],
        "--normalize": [True, False],
        "--solver": ['svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga'],
        "-ns": [100, 200, 300],
        "-nf": [10, 20, 30]
    }
elif args.tool == "time" or args.tool == "perf":
    arg_dict = {
        "--fit_intercept": [True, False],
        "--normalize": [True, False],
        "--solver": ['svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga'],
        "-ns": [10000, 100000, 1000000],
        "-nf": [100, 1000, 10000]
    }

arg_grid = ParameterGrid(arg_dict)

config_filename = "bench_ridge.{}cfg".format(args.tool)
write_config_file(config_filename, arg_grid)
