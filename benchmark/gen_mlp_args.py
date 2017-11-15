"""
Generate argument list for benchmark MLP
"""

from sklearn.model_selection import ParameterGrid
from util import dict_to_str
import argparse

parser = argparse.ArgumentParser(description="Generate configuration file for bench_mlp")
parser.add_argument("tool", help="configuration for which tool", choices=["time", "perf", "pin"])
args = parser.parse_args()

if args.tool == "pin":
    arg_dict = {
        "--activation": ["logistic", "tanh", "relu"],
        "--solver": ["lbfgs", "sgd", "adam"],
        "--learning_rate": ["constant", "invscaling", "adaptive"],
        "--shuffle": [True, False],
        "-ns": [100, 400, 1600],
        "-nf": [10, 40, 160]
    }
elif args.tool == "time" or args.tool == "perf":
    arg_dict = {
        "--activation": ["logistic", "tanh", "relu"],
        "--solver": ["lbfgs", "sgd", "adam"],
        "--learning_rate": ["constant", "invscaling", "adaptive"],
        "--shuffle": [True, False],
        "-ns": [10000, 100000, 1000000],
        "-nf": [100, 1000, 10000]
    }

arg_grid = ParameterGrid(arg_dict)

config_filename = "bench_mlp.{}cfg".format(args.tool)

with open(config_filename, "w") as f:
    for arg in arg_grid:
        # learning_rate: only used when solver="sgd"
        if arg["--solver"] != "sgd" and arg["--learning_rate"] != "constant":
            continue
        
        # shuffle: Only used when solver="sgd" or "adam"
        if arg["--shuffle"] and arg["--solver"] == "lbfgs":
            continue

        if (arg["-ns"] * arg["-nf"] <= 100000000):
            f.write(dict_to_str(arg)+"\n")
