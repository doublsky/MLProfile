"""
Profile all bench_list
"""

import subprocess as sp
import pandas as pd
import argparse

rpt_cmd = "opreport -l -n -t 5".split()

# results dataframe
results_df = pd.DataFrame()
idx = 0

# read a list of interested kernels
kernel_list = pd.read_table("kernel_list.txt", header=None, names=["kernel"])
kernel_exc_list = pd.read_table("kernel_exc_list.txt", header=None, names=["kernel"])

def trim_func_param(infile, outfile):
    with open(infile, 'r') as inf, open (outfile, 'w') as outf:
        for line in inf:
            remainder = line.split('(')[0]
            outf.write(remainder+"\n")


def process_rpt(rpt, bench):
    global results_df, idx

    # read results into a datafram
    rpt_df = pd.read_table(rpt, delim_whitespace=True, header=None, index_col=False,
        names=["samples", "percent", "image_name", "app_name", "symbol_name"])

    # write workload name
    workload_name = bench.replace(".py", "").replace("bench_", "")
    results_df.set_value(idx, "workload", workload_name)

#    # look for interested kernels
#    for kernel in kernel_list["kernel"]:
#        # find corresponding entry
#        #target = rpt_df[rpt_df["symbol_name"] == kernel]
#        target = rpt_df[rpt_df["symbol_name"].str.contains(kernel)]
#        # add to results
#        if (target.empty):
#            results_df.set_value(idx, kernel, 0)
#        elif (target.shape[0] == 1):
#            results_df.set_value(idx, kernel, target.iloc[0].loc["percent"])
#        else:
#            raise Exception("Duplicated symbols in profiling results")

    # exclude non-interested kernels
    for kernel in kernel_exc_list['kernel']:
        rpt_df = rpt_df[~(rpt_df["symbol_name"].str.contains(kernel))]

    # copy rest kernels
    for _, row in rpt_df.iterrows():
        results_df.set_value(idx, row['symbol_name'], row['percent'])

    # move to next record
    idx += 1


def run_bench(bench):
    global args
    test_cmd = ['timeout', '-k', '3', '3', 'python', bench]
    perf_cmd = ['operf', 'timeout', '-k', args.timeout, args.timeout, 'python', bench]

    with open(bench.replace(".py", ".args"), 'r') as arg_list:
        for perf_arg in arg_list:
            if (args.test):
                ret = sp.call(test_cmd + perf_arg.split())
                if (ret != 0 and ret != 124):
                    raise Exception("Cmd failed with "+str(ret)+", args: "+perf_arg)
            else:
                sp.check_call(perf_cmd + perf_arg.split())
                sp.check_call(rpt_cmd + ["-o", "/tmp/blasrpt.tmp"])
                trim_func_param("/tmp/blasrpt.tmp", "/tmp/blasrpt_trimmed.tmp")
                process_rpt("/tmp/blasrpt_trimmed.tmp", bench)

# main
parser = argparse.ArgumentParser(description='Run benchmarks, collect data.')
parser.add_argument('--bench_list', default='bench_list.txt', type=str,
    help='path to a file containing a list of benchmarks.')
parser.add_argument('--kernel_list', default='kernel_list.txt', type=str,
    help='path to a file containing a list of kernels.')
parser.add_argument('--timeout', default='60', type=str,
    help='Maximum execution time (in sec) allowed for each benchmark.')
parser.add_argument('--test', action='store_true',
    help='Test benchmarks, do not profile.')
parser.add_argument('--output', default='data.csv', type=str,
    help='path to output file.')
args = parser.parse_args()

# iterate through all benchmarks
with open(args.bench_list, 'r') as bench_list:
    for bench in bench_list:
        if not (bench.startswith("#")):
            run_bench(bench.rstrip())

# write results
results_df.to_csv(args.output, index=False)
