"""
Profile all bench_list
"""

import subprocess as sp
import pandas as pd
import argparse
from util import *

rpt_cmd = "opreport -l -n -t 5".split()


# results dataframe
# results_df = pd.DataFrame()
# idx = 0

# read a list of interested kernels

def trim_func_param(infile, outfile):
    with open(infile, 'r') as inf, open(outfile, 'w') as outf:
        for line in inf:
            remainder = line.split('(')[0]
            outf.write(remainder + "\n")


def process_rpt(rpt):
    global results_df, idx

    # read results into a datafram
    rpt_df = pd.read_table(rpt, delim_whitespace=True, header=None, index_col=False,
                           names=["samples", "percent", "image_name", "app_name", "symbol_name"])

    # exclude non-interested kernels
    for kernel in kernel_exc_list['kernel']:
        rpt_df = rpt_df[~(rpt_df["symbol_name"].str.contains(kernel))]

    # copy rest kernels
    for _, row in rpt_df.iterrows():
        results_df.set_value(idx, row['symbol_name'], row['percent'])

    # move to next record
    idx += 1


def perf_bench(cmdargs, benchfile):
    test_cmd = ['timeout', '-k', '3', '3', 'python', benchfile]
    #perf_cmd = ['operf', '--event=CPU_CLK_UNHALTED:300000', 'timeout', '-k', cmdargs.timeout, '-s', '9', args.timeout,
    #            'python', benchfile]
    perf_cmd = ['operf', 'python', benchfile]

    with open(get_argfile(benchfile), 'r') as arg_list:
        for perf_arg in arg_list:
            if (cmdargs.test):
                ret = sp.call(test_cmd + perf_arg.split())
                if ret != 0 and ret != 124:
                    raise Exception("Cmd failed with " + str(ret) + ", args: " + perf_arg)
            else:
                sp.check_call(perf_cmd + perf_arg.split())
                sp.check_call(rpt_cmd + ["-o", "/tmp/blasrpt.tmp"])
                trim_func_param("/tmp/blasrpt.tmp", "/tmp/blasrpt_trimmed.tmp")
                process_rpt("/tmp/blasrpt_trimmed.tmp")


def time_bench(cmdargs, benchfile):
    cmd = ['/usr/bin/time', '-a', '-o', cmdargs.output, 'python'] + [benchfile]
    with open(get_argfile(benchfile), 'r') as argfile:
        for line in argfile:
            arg_list = line.split()
            sp.check_call(cmd + arg_list)


# top level parser
parser = argparse.ArgumentParser(description='Run benchmarks, collect data.')
parser.add_argument('--blist', default='bench_list.txt',
                    help='path to benchmark list')
subparsers = parser.add_subparsers(help='available sub-command')

# parser for time
parser_time = subparsers.add_parser('time', help='time each benchmark')
parser_time.add_argument('--output', default='time.rpt', help="path to output report")
parser_time.set_defaults(func=time_bench)

# parser for operf
parser_perf = subparsers.add_parser('perf', help='profile using operf')
parser.add_argument('--klist', default='kernel_list.txt',
                    help='path to kernel list')
parser.add_argument('--kexclude', action='store_true',
                    help='exclude kernels in klist')
parser.add_argument('--timeout', default='60', type=str,
                    help='Maximum execution time (in sec) allowed for each benchmark.')
parser.add_argument('--test', action='store_true',
                    help='Test benchmarks, do not profile.')
parser.add_argument('--tool', default='time', choices=['time', 'perf', 'pin'],
                    help='select which tool to use to profile')
args = parser.parse_args()

with open(args.klist, 'r') as klist_file:
    kernel_list = klist_file.readlines()
    kernel_list = map(lambda x: x.rstrip(), kernel_list)

# iterate through all benchmarks
with open(args.blist, 'r') as bench_list:
    for bench in bench_list:
        if not (bench.startswith("#")):  # allow commenting in benchmark list
            # init
            results_df = pd.DataFrame()
            idx = 0
            bench = "benchmark/" + bench.rstrip()

            try:
                # run
                # run_bench(bench)
                args.func(args, bench)

            finally:
                # post processing (generate signature)
                for index, row in results_df.iterrows():
                    sig = get_series_signature(row)
                    results_df.set_value(index, 'signature', sig)

                # export to .csv
                if (not args.test):
                    results_df.to_csv(bench.replace('.py', '.csv'), index=False)
