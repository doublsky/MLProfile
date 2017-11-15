"""
Generate argument list for benchmark logistic regression.
"""

from sklearn.model_selection import ParameterGrid
from util import dict_to_str
import argparse

parser = argparse.ArgumentParser(description="Generate configuration file for bench_logistic")
parser.add_argument("tool", help="configuration for which tool", choices=["time", "perf", "pin"])
args = parser.parse_args()

if args.tool == "pin":
    arg_dict = {
        "--penalty": ["l1", "l2"],
        "--dual": [True, False],
        "--fit_intercept": [True, False],
        "--solver": ["newton-cg", "lbfgs", "liblinear", "sag", "saga"],
        "--multi_class": ["ovr", "multinomial"],
        "-ns": [100, 200, 300],
        "-nf": [10, 20, 30]
    }
elif args.tool == 'time' or args.tool == 'perf':
    arg_dict = {
        "--penalty": ["l1", "l2"],
        "--dual": [True, False],
        "--fit_intercept": [True, False],
        "--solver": ["newton-cg", "lbfgs", "liblinear", "sag", "saga"],
        "--multi_class": ["ovr", "multinomial"],
        "-ns": [10000, 100000, 1000000],
        "-nf": [100, 1000, 10000]
    }

arg_grid = ParameterGrid(arg_dict)

config_filename = 'bench_logistic.{}cfg'.format(args.tool)

with open(config_filename, "w") as f:
    for arg in arg_grid:
        # The "newton-cg", "sag" and "lbfgs" solvers support only l2 penalties
        if arg["--penalty"] == "l1" and arg["--solver"] in ["newton-cg", "sag", "lbfgs"]:
            continue
        
        # Dual formulation is only implemented for l2 penalty with liblinear solver
        if arg["--dual"] and (arg["--penalty"] != "l2" or arg["--solver"] != "liblinear"):
            continue
        
        # Prefer dual=False when n_samples > n_features
        if arg["--dual"] and arg["-ns"] > arg["-nf"]:
            continue
        
        # only "newton-cg", "sag", "saga" and "lbfgs" handle multinomial loss
        if arg["--multi_class"] == "multinomial" and arg["--solver"] not in ["newton-cg", "sag", "saga", "lbfgs"]:
            continue
        
        # "newton-cg", "lbfgs" and "sag" only handle L2 penalty
        if arg["--solver"] in ["newton-cg", "lbfgs", "sag"] and arg["--penalty"] == "l1":
            continue
    
        if (arg["-ns"] * arg["-nf"] <= 100000000):
            f.write(dict_to_str(arg)+"\n")
