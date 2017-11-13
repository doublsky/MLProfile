"""
Utilities for sklearn BLAS profiling.
"""

import argparse
import pandas as pd
import numpy as np
import os
import re


def gen_bench_list(bench_dir):
    all_files = os.listdir(bench_dir)
    pattern = re.compile("bench_.*\.py")
    bench_list = [x for x in all_files if re.match(pattern, x)]
    return bench_list


def gen_blist_file(args):
    bench_list = gen_bench_list(args.bench_dir)
    with open(args.output, "w") as f:
        f.write("\n".join(bench_list)+"\n")


def dict_to_str(input_dict):
    return " ".join("{} {}".format(key, val) for key, val in input_dict.items())


def write_config_file(filename, configs):
    with open(filename, "w") as f:
        for config in configs:
            if (config["-ns"] * config["-nf"] < 1e8+1):
                f.write(dict_to_str(config)+"\n")


def gen_dataset(RorC, ns, nf):
    # imports
    from sklearn.datasets.samples_generator import make_regression, make_classification

    # get path to project root
    MLProf_root = os.environ["MLPROF_ROOT"]

    if RorC == "reg":
        X, y = make_regression(n_samples=ns,
                               n_features=nf,
                               n_informative=nf//2,
                               noise=0.1)
    elif RorC == "cl2":
        X, y = make_classification(n_samples=ns,
                                   n_features=nf,
                                   n_informative=nf//2,
                                   n_redundant=nf//10,
                                   n_classes=2)
    elif RorC == "cl3":
        X, y = make_classification(n_samples=ns,
                                   n_features=nf,
                                   n_informative=nf//2,
                                   n_redundant=nf//10,
                                   n_classes=3)
    else:
        raise ValueError("RorC must be either reg, cl2, or cl3, got " + str(RorC))
    
    X_name = "{}X_ns{}_nf{}".format(RorC, ns, nf)
    X_path = os.path.join(MLProf_root, "dataset", X_name)
    np.save(X_path, X)
    y_name = "{}y_ns{}_nf{}".format(RorC, ns, nf)
    y_path = os.path.join(MLProf_root, "dataset", y_name)
    np.save(y_path, y)

    newX = np.load(X_path+".npy")
    newy = np.load(y_path+".npy")

    assert np.array_equal(newX, X)
    assert np.array_equal(newy, y)


def maybe_create_dataset(config_line):
    parser = argparse.ArgumentParser()
    parser.add_argument("-ns", type=int)
    parser.add_argument("-nf", type=int)
    configs, _ = parser.parse_known_args(config_line.split())

    MLProf_root = os.environ["MLPROF_ROOT"]
    dataset_dir = os.path.join(MLProf_root, "dataset")

    # maybe create dataset dir
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    for prefix in ["regX", "regy", "cl2X", "cl2y", "cl3X", "cl3y"]:
        dataset_name = "{}_ns{}_nf{}.npy".format(prefix, configs.ns, configs.nf)
        dataset_path = os.path.join(dataset_dir, dataset_name)

        if not os.path.exists(dataset_path):
            gen_dataset(prefix[0:3], configs.ns, configs.nf)


def get_config_file(benchfile, prof_type):
    old_style_config_file = benchfile.replace(".py", ".args")
    if os.path.exists(old_style_config_file):
        return old_style_config_file
    else:
        return benchfile.replace(".py", ".{}cfg".format(prof_type))


def get_argfile(benchfile):
    return get_config_file(benchfile)


def str2bool(s):
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def get_series_signature(series):
    ret = ""
    for _, value in series.iteritems():
        if pd.isnull(value):
            ret += "0"
        else:
            ret += "1"
    return int(ret, 2)


def post_processing(df):
    df.drop("workload", axis=1, inplace=True)
    for index, row in df.iterrows():
        sig = get_series_signature(row)
        df.set_value(index, "signature", sig)


def post_proc(args):
    df = pd.read_csv(args.input, index_col=False)
    post_processing(df)
    df.to_csv(args.o, index=False)


def gen_klist(args):
    data_df = pd.read_excel(args.input, sheetname="Dict")
    data_df["Kernel Name"].to_csv(args.outtxt, header=False, index=False)
    with open(args.outhead, "w") as f:
        f.write("#define KERNEL_SIZE " + str(data_df.shape[0]) + "\n")
        f.write("char* kernel_list[] = {\n")
        for _, row in data_df.iterrows():
            f.write('    "' + row["Kernel Name"] + '",\n')
        f.write('    "dummy"\n}; \n')


def arg2csv(infile):
    result = pd.DataFrame()
    idx = 0

    with open(infile, "r") as argf:
        for line in argf:
            argslist = line.split()
            for key, value in zip(argslist[0::2], argslist[1::2]):
                result.set_value(idx, re.sub("^-+", "", key), value)
            idx += 1

    return result


def arg2csv_intf(args):
    result_df = arg2csv(args.argfile)
    result_df.to_csv(args.csvfile, index=False)


def find_dep(args):
    addr_dict = {}
    kernel_set = set()
    with open(args.trace, "r") as f:
        for line in f:
            kernel, rw, addr = line.split()
            kernel_set.add(kernel)
            if addr in addr_dict:
                addr_dict[addr].append((kernel, rw))
            else:
                addr_dict[addr] = [(kernel, rw)]

    dep_dict = {}

    for k1 in kernel_set:
        for k2 in kernel_set:
            dep_dict[k1, k2] = 0

    for addr in addr_dict:
        writer = ""
        for kernel, rw in addr_dict[addr]:
            if rw == "W":
                writer = kernel
            if rw == "R" and writer != "":
                dep_dict[writer, kernel] += 1

    for k1 in kernel_set:
        for k2 in kernel_set:
            print k1, "to", k2, ":", dep_dict[k1, k2]


def parse_trace(tracefile):
    owner = {}
    comm_matrix = {}

    with tracefile as trace:
        for line in trace:
            kernel, num_calls, rw, addr, size = line.split()
            size = int(size)
            addr_int = int(addr, 16)
            
            # writer immediately becomes the owner
            if rw == "W":
                # foreach byte
                for i in range(0, size):
                    effective_addr = hex(addr_int+i)
                    owner[effective_addr] = (kernel, "W")

            # first assume everything goes to memory
            if rw == "R":
                if ("memory", kernel) in comm_matrix:
                    comm_matrix["memory", kernel] += size
                else:
                    comm_matrix["memory", kernel] = size
            elif rw == "W":
                if (kernel, "memory") in comm_matrix:
                    comm_matrix[kernel, "memory"] += size
                else:
                    comm_matrix[kernel, "memory"] = size
            else:
                raise Exception("Unknown memory operation in trace, line: " + line)

            # now consider comm/locality
            if rw == "R":
                # foreach byte
                for i in range(0, size):
                    effective_addr = hex(addr_int+i)
                    if effective_addr in owner:
                        if owner[effective_addr][1] == "W":
                            comm_matrix[owner[effective_addr][0], "memory"] -= 1
                        comm_matrix["memory", kernel] -= 1
                        if (owner[effective_addr][0], kernel) in comm_matrix:
                            comm_matrix[owner[effective_addr][0], kernel] += 1
                        else:
                            comm_matrix[owner[effective_addr][0], kernel] = 1
                        owner[effective_addr] = (kernel, "R")

    return comm_matrix


if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Utilities for BLAS profiling.")
    subparsers = parser.add_subparsers(title="available sub-command")

    # post_process
    parser_pp = subparsers.add_parser("post_proc", help="generate signature for each use case")
    parser_pp.add_argument("input", type=str, help="Path to input .csv file")
    parser_pp.add_argument("-o", default="data.csv", type=str,
                           help="Path to output .csv file")
    parser_pp.set_defaults(func=post_proc)

    # generate kernel list
    parser_klist = subparsers.add_parser("klist", help="extract all kernels from input Excel file")
    parser_klist.add_argument("input", type=str, help="path to input excel file")
    parser_klist.add_argument("--outtxt", default="kernel_list.txt", type=str, help="path to output file")
    parser_klist.add_argument("--outhead", default="kernel_list.h", type=str, help="path to output file")
    parser_klist.set_defaults(func=gen_klist)

    # convert .args file to .csv file
    parser_a2c = subparsers.add_parser("arg2csv", help="convert a bench_<app>.args file to .csv format")
    parser_a2c.add_argument("argfile", type=str, help="Path to input .args file")
    parser_a2c.add_argument("csvfile", type=str, help="Path to output .csv file")
    parser_a2c.set_defaults(func=arg2csv_intf)

    # find dependency 
    parser_dep = subparsers.add_parser("depend", help="find dependency among kernels")
    parser_dep.add_argument("--trace", default="procatrace.out", help="path to trace file")
    parser_dep.set_defaults(func=find_dep)
    
    # generate bench_list file
    parser_blist = subparsers.add_parser("blist", help="generate bench_list file")
    parser_blist.add_argument("--bench_dir", default="benchmark", help="path to benchmark directory")
    parser_blist.add_argument("--output", default="bench_list.txt", help="path to output bench_list file")
    parser_blist.set_defaults(func=gen_blist_file)

    args = parser.parse_args()
    args.func(args)
