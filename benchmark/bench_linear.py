"""
Benchmark Linear Regression

"""
from util import *
import numpy as np
import argparse
from time import time
from sklearn import linear_model
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark ordinary linear regression.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--fit_intercept', default=True, type=str2bool,
                        help="parameter for underlying linear regression.")
    parser.add_argument('--normalize', default=False, type=str2bool,
                        help="parameter for underlying linear regression.")
    args = parser.parse_args()

    print >> sys.stderr, "- loading data..."
    start_time = time()
    X_name = "dataset/regX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/regy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print >> sys.stderr, "- data loading time:", data_loading_time
    print >> sys.stderr, "- benchmark ordinary linear regression..." 
    regr = linear_model.LinearRegression(copy_X=False, normalize=args.normalize, fit_intercept=args.fit_intercept)
    start_time = time()
    regr.fit(X, y)
    fit_time = time() - start_time
    print >> sys.stderr, "- benchmark finished, fitting time:", fit_time
