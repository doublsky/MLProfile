"""
Profile all bench_list
"""

import subprocess as sp
import pandas as pd

rpt_cmd = "opreport -l -n -t 5".split()

# results dataframe
results_df = pd.DataFrame()
idx = 0

# read a list of bench_xxx.py
bench_list = pd.read_table("bench_list.txt", delim_whitespace=True,
    header=None, names=["bench"])

# read a list of interested kernels
kernel_list = pd.read_table("kernel_list.txt", header=None, names=["kernel"])

def process_rpt(rpt, args, bench):
    # clarify global variables
    global results_df, idx
    # convert results into a datafram
    rpt_df = pd.read_table(rpt, delim_whitespace=True, header=None,
        names=["samples", "percent", "image_name", "symbol_name"])
    # write workload name
    workload_name = bench.replace(".py", "").replace("bench_", "")
    results_df.set_value(idx, "workload", workload_name)
    # find kernels from libopenblas
#    lib_name = "libopenblasp-r0-39a31c03.2.18.so"
#    libopenblas_kernels = rpt_df[rpt_df["image_name"] == lib_name]
#    for _, row in libopenblas_kernels.iterrows():
#        results_df.set_value(idx, row["symbol_name"], row["percent"])
#    # take out libopenblas
#    rest_rpt = rpt_df[rpt_df["image_name"] != lib_name]
    # look for interested kernels
    for kernel in kernel_list["kernel"]:
        # find corresponding entry
        target = rpt_df[rpt_df["symbol_name"] == kernel]
        # add to results
        if (target.empty):
            results_df.set_value(idx, kernel, 0)
        elif (target.shape[0] == 1):
            results_df.set_value(idx, kernel, target.iloc[0].loc["percent"])
        else:
            raise Exception("Duplicated symbol names in profiling results")

    # write execution time to results
    exe_time = pd.read_table(bench.replace(".py", ".time"), delim_whitespace=True,
        header=None, names=["fitting_time"])
    for t in exe_time.columns:
        results_df.set_value(idx, t, exe_time.iloc[0].loc[t])
    # write arguments to results
    for param in args.index:
        results_df.set_value(idx, param, args[param])
    # move to next record
    idx += 1
    

# iterate through all bench
for bench in bench_list["bench"]:
    if bench.startswith("#"):
        continue
    # beginning of profiling cmd
    perf_cmd = ["operf", "python", bench]
    # read a list of arguments of this bench
    arg_list = pd.read_table(bench.replace(".py", ".args"), delim_whitespace=True)
    # for each of arguments combination
    for _, row in arg_list.iterrows():
        # concat all arguments/parameters
        args = []
        for param in arg_list.columns:
            if (row[param] == 'empty_str'):     #should skip
                continue
            args.append(param)
            if (param == "-ns"):
                args.append(str(int(row[param])))
            elif (param == "-nf"):
                args.append(str(int(row[param])))
            elif (param == "--solver"):
                args.append(row[param])
            elif (param == "--precompute"):
                args.append(str(row[param]))
            else:
                raise Exception("Unexpected argument name" + param)
        # debug cmd
        #print perf_cmd + args
        #print rpt_cmd
        # run profiling
        sp.check_call(perf_cmd + args)
        # retrieve profiling results
        rpt = sp.check_output(rpt_cmd + ["-o", "/tmp/blasrpt.tmp"])
        # process results
        process_rpt("/tmp/blasrpt.tmp", row, bench)
# write results
results_df.to_csv("data.csv", index=False)
