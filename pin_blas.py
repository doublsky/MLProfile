"""
Run Pin for all benchmarks
"""

import argparse
import os
import subprocess as sp
from util import *
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Pin, generate memory reference trace.")
    parser.add_argument("--blist", default="bench_list.txt", help="path to benchmark list file")
    parser.add_argument("--output", default="pin_out", help="path to output directory")
    args = parser.parse_args()

    # force numpy to run in single thread
    os.environ["OMP_NUM_THREADS"] = "1"

    # get pin root
    pin_home = os.environ["PIN_ROOT"]

    pin_cmd = [pin_home+"/pin", "-t", pin_home+"/source/tools/pintools/obj-intel64/procatrace.so", "--", "python"]

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # iterate through all benchmarks
    with open(args.blist, "r") as bench_list:
        for bench in bench_list:
            if not (bench.startswith("#")):     # allow commenting in benchmark list
                # init
                bench = bench.rstrip()
                benchfile = "benchmark/" + bench
                config_file = get_config_file(benchfile)
                count = 0

                with open(config_file, 'r') as config_list:
                    for configs in config_list:
                        # init
                        outfile = bench.replace(".py", "_"+str(count)+".trace")

                        # call pin
                        #pin = sp.Popen(pin_cmd + [benchfile] + configs.split(), stdout=sp.PIPE)
                        sp.check_call(pin_cmd + [benchfile] + configs.split())

                        # parse results
                        #mem_read, mem_write, comm = parse_trace(pin.stdout)

                        ''''# format results
                        results_df = pd.DataFrame()
                        for key, value in comm.iteritems():
                            results_df.set_value(key[0], key[1], value)
                        for index in results_df.index:
                            results_df.set_value(index, "mem_read", mem_read[index])
                            results_df.set_value(index, "mem_write", mem_write[index])

                        # save results
                        results_df.to_csv(os.path.join(args.output, outfile))
                        count += 1'''
