"""
Profile all bench_list
"""

import subprocess as sp
import pandas as pd
import argparse
from util import *

rpt_cmd = "opreport -l -n".split()


# results dataframe
# results_df = pd.DataFrame()
# idx = 0

# read a list of interested kernels

def trim_func_param(infile, outfile):
    with open(infile, "r") as inf, open(outfile, "w") as outf:
        for line in inf:
            remainder = line.split("(")[0]
            outf.write(remainder + "\n")


def process_rpt(rpt, results_df, idx):
    # global results_df, idx

    # read results into a datafram
    rpt_df = pd.read_table(rpt, delim_whitespace=True, header=None, index_col=False,
                           names=["samples", "percent", "image_name", "symbol_name"])

    # select kernels / exclude kernels
    if args.kexclude:
        for kernel in kernel_list:
            rpt_df = rpt_df[~(rpt_df["symbol_name"].str.contains(kernel))]

    # copy rest kernels
    for _, row in rpt_df.iterrows():
        if args.kexclude:
            results_df.set_value(idx, row["symbol_name"], row["percent"])
        else:
            if row["symbol_name"] in kernel_list:
                results_df.set_value(idx, row["symbol_name"], row["percent"])

    # move to next record
    return idx + 1


def test_bench(args):
    # iterate through all benchmarks
    with open(args.blist, "r") as bench_list:
        for bench in bench_list:
            if bench.startswith("#"):  # allow commenting in benchmark list
                continue

            test_cmd = ["timeout", "-k", "3", "3", "python", benchfile]
            config_file = get_config_file(benchfile, args.tool)
            
            with open(config_file, "r") as config_list, open(args.output, "w") as outfile:
                for config in config_list:
                    maybe_create_dataset(config)
                    sp.call(test_cmd + config.split(), stdout=outfile, stderr=outfile)


def perf_bench(args):
    # iterate through all benchmarks
    with open(args.blist, "r") as bench_list:
        for bench in bench_list:
            if bench.startswith("#"):  # allow commenting in benchmark list
                continue
            
            # init
            benchfile = "benchmark/" + bench.rstrip()
            perf_cmd = ["operf", "--event=CPU_CLK_UNHALTED:300000", "python", benchfile]
            results_df = pd.DataFrame()
            idx = 0

            with open(get_config_file(benchfile, "perf"), "r") as config_list:
                for config in config_list:
                    maybe_create_dataset(config)
                    try:
                        sp.check_call(perf_cmd + config.split())
                        sp.check_call(rpt_cmd + ["-o", "/tmp/blasrpt.tmp"])
                        trim_func_param("/tmp/blasrpt.tmp", "/tmp/blasrpt_trimmed.tmp")
                        idx = process_rpt("/tmp/blasrpt_trimmed.tmp", results_df, idx)
                    finally:
                        # post processing (generate signature)
                        for index, row in results_df.iterrows():
                            sig = get_series_signature(row)
                            results_df.set_value(index, "signature", sig)

                        # export to .csv
                        results_df.to_csv(benchfile.replace(".py", ".csv"), index=False)


def time_bench(args):
    # iterate through all benchmarks
    with open(args.blist, "r") as bench_list:
        for bench in bench_list:
            if bench.startswith("#"):  # allow commenting in benchmark list
                continue
                
            # init
            benchfile = "benchmark/" + bench.rstrip()
            time_output = benchfile.replace(".py", ".time")
            cmd = ["/usr/bin/time", "-a", "-o", time_output, "python"] + [benchfile]
            
            # foreach configuration
            with open(get_config_file(benchfile, "time"), "r") as config_file:
                for config in config_file:
                    maybe_create_dataset(config)
                    sp.check_call(cmd + config.split())


def trace2csv(csvfile, count, mem_rd, mem_wr, comm_mat):
    with open(csvfile, "a") as resutls:
        resutls.write("use case,producer,consumer,data\n")
        
        for key, value in mem_rd.iteritems():
            resutls.write("{},memory,{},{}".format(count, key, value))

        for key, value in mem_wr.iteritems():
            resutls.write("{},{},memory,{}".format(count, key, value))

        for key, value in comm_mat.iteritems():
            resutls.write("{},{},{},{}".format(count, key[0], key[1], value))



def pin_bench(args):
    # force numpy to run in single thread
    os.environ["OMP_NUM_THREADS"] = "1"
    
    # get pin root
    pin_home = os.environ["PIN_ROOT"]
    
    pin_cmd = [pin_home+"/pin", "-t", "pintools/obj-intel64/procatrace.so"]
    
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # iterate through all benchmarks
    with open(args.blist, "r") as bench_list:
        for bench in bench_list:
            if bench.startswith("#"):     # allow commenting in benchmark list
                continue
                
            # init
            bench = bench.rstrip()
            benchfile = "benchmark/" + bench
            config_file = get_config_file(benchfile, "pin")
            count = 0
            
            with open(config_file, 'r') as config_list:
                for configs in config_list:
                    # init
                    tracefile = bench.replace(".py", "_config"+str(count)+".trace")
                    tracefile = os.path.join(args.outdir, tracefile)
                    
                    # skip profile if output file exist
                    if not os.path.exists(tracefile):
                        # create dataset if not exist
                        maybe_create_dataset(configs)
                        
                        # call pin
                        full_cmd = pin_cmd
                        full_cmd += ["-output", tracefile, "--", "python", benchfile]
                        full_cmd += configs.split()
                        sp.check_call(full_cmd)
                
                    with open(tracefile, "r") as trace:
                        mem_rd, mem_wr, comm_mat = parse_trace(trace)
                    
                    outfile = benchfile.replace(".py", "_pin.csv")
                    trace2csv(outfile, count, mem_rd, mem_wr, comm_mat)
                    
                    count += 1



if __name__ == "__main__":
    # top level parser
    parser = argparse.ArgumentParser(description="Run benchmarks, collect data")
    parser.add_argument("--blist", default="bench_list.txt", help="path to benchmark list")
    subparsers = parser.add_subparsers(help="available sub-command")

    # parser for time
    parser_time = subparsers.add_parser("time", help="time each benchmark")
    parser_time.set_defaults(func=time_bench)

    # parser for operf
    parser_perf = subparsers.add_parser("perf", help="profile using operf")
    parser_perf.add_argument("--klist", default="kernel_list.txt", help="path to kernel list")
    parser_perf.add_argument("--kexclude", action="store_true", help="exclude kernels in klist")
    parser_perf.add_argument("--test", action="store_true", help="Test benchmarks, do not profile.")
    parser_perf.set_defaults(func=perf_bench)

    # parser for pin
    parser_pin = subparsers.add_parser("pin", help="run Pin, generate memory reference trace")
    parser_pin.add_argument("--klist", default="kernel_list.txt", help="path to kernel list file")
    parser_pin.add_argument("--outdir", default="/scratchl/ttan/pin_out", help="path to output directory")
    parser_pin.set_defaults(func=pin_bench)
    
    # parser for test
    parser_test = subparsers.add_parser("test", help="test validity of benchmark configurations")
    parser_test.add_argument("--tool", default="perf", choices=["time", "perf", "pin"], help="for which tool")
    parser_test.add_argument("--output", default="test.log", help="path to test results file")
    parser_test.set_defaults(func=test_bench)
    
    # parser command-line args
    args = parser.parse_args()

    with open(args.klist, "r") as klist_file:
        kernel_list = klist_file.readlines()
        kernel_list = map(lambda x: x.rstrip(), kernel_list)

    args.func(args)
