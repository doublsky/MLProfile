"""
Utilities for BLAS profiling.
"""

import argparse
import pandas as pd

def str2bool(s):
    if (s == 'True'):
        return True
    elif (s == 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def hash_pd_series(series):
    ret = ''
    for _, value in series.iteritems():
        if (pd.isnull(value)):
            ret += '0'
        else:
            ret += '1'
    return int(ret, 2)
