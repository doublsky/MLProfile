"""
Drawing utilities for sklearn BLAS profiling
"""

import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def l1norm(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def eval_mem(args):
    workload = pd.read_csv(args.comm_pat, index_col=0)
    locM = (0, 0)
    
    def calc_ratio(layoutfile):
        layout = pd.read_csv(layoutfile, index_col=0)
        results = pd.DataFrame()
    
        for row_index, row in workload.iterrows():
            asic_total = 0
            fpga_total = 0
            fpga_dist = iter([1,1,2,2,2,3])
            for index, value in row.iteritems():
                if pd.notnull(value):
                    if (index in layout.index):
                        asic_total += value / 100 * l1norm(locM, (layout.loc[index, 'locX'], layout.loc[index, 'locY']))
                    else:
                        asic_total += value / 100 * 3
                    fpga_total += value / 100 * fpga_dist.next()
            results.set_value(row_index, 'asic', asic_total)
            results.set_value(row_index, 'fpga', fpga_total)
            if (fpga_total == 0):
                results.set_value(row_index, 'ratio', 1)
            else:
                results.set_value(row_index, 'ratio', asic_total / fpga_total)
        return results['ratio'].values
    
    for layout, label in zip(args.layouts, args.labels):
        ratio = calc_ratio(layout)
        sns.distplot(ratio, hist=False, label=label)
    
    plt.xlabel('Hard-to-soft communication distance ratio')
    plt.ylabel('Probability density')
    plt.show()

def compare_layout(args):
    layout = pd.read_csv(args.layout, index_col=0)
    workload = pd.read_csv(args.comm_pat, index_col=0)
    
    def total_dist(tiles):
        tmp_list = list(tiles)
        dist_sum = 0
        for i in range(len(tmp_list)-1):
            dist_sum = l1norm(tmp_list[i], tmp_list[i+1])
        return dist_sum
    
    for row_index, row in workload.iterrows():
        asic_tiles = set()
        fpga_tiles = 0
        for index, value in row.iteritems():
            if pd.notnull(value):
                if (index in layout.index):
                    asic_tiles.add((layout.loc[index, 'locX'], layout.loc[index, 'locY']))
                else:
                    asic_tiles.add((0,2))
                fpga_tiles += 1
        workload.set_value(row_index, 'asic', len(asic_tiles))
        workload.set_value(row_index, 'fpga', fpga_tiles)
    print workload[['asic', 'fpga']]
    
    sns.distplot(workload['asic'].values, bins=3, kde=False, label='ASIC')
    sns.distplot(workload['fpga'].values, bins=6, kde=False, label='FPGA')
    plt.xlabel('Number of tiles used')
    plt.ylabel('Number of applications')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Drawing utilities for sklearn BLAS profiling.')
    subparsers = parser.add_subparsers(title='available sub-command')

    # compare FPGA layout and ASIC layout
    parser_cmp = subparsers.add_parser('compare', help='given an ASIC layout, compare FPGA and ASIC')
    parser_cmp.add_argument('--comm_pat', type=str, default='comm_pat.csv', help='path to communication pattern file')
    parser_cmp.add_argument('--layout', type=str, default='layout.csv', help='path to ASIC layout file')
    parser_cmp.set_defaults(func=compare_layout)

    # evaluate memory distance
    parser_mem = subparsers.add_parser('eval_mem', help='evaluate memory distance')
    parser_mem.add_argument('--comm_pat', type=str, default='comm_pat.csv', help='path to communication pattern file')
    parser_mem.add_argument('--layouts', default='layout.csv', nargs='+', help='a list of layout.csv files')
    parser_mem.add_argument('--labels', default='Case 1', nargs='+', help='a list of labels for layouts')

    args = parser.parse_args()
    args.func(args)
