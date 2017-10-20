"""
Benchmark Gradient Boost
"""

from util import *
import numpy as np
import argparse
from time import time
from sklearn import ensemble
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark gradient boost.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--loss', default='deviance', type=str,
                        help="parameter for underlying gradient boost.")
    parser.add_argument('--criterion', default='friedman_mse', type=str,
                        help="parameter for underlying gradient boost.")
    parser.add_argument('--presort', default=False, type=str2bool,
                        help="parameter for underlying gradient boost.")
    args = parser.parse_args()

    print >> sys.stderr, "- loading data..."
    start_time = time()
    X_name = "dataset/clfX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    if args.loss == 'exponential':
        X_name = X_name.replace('.npy', '_c2.npy')
    X = np.load(X_name)
    y_name = "dataset/clfy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    if args.loss == 'exponential':
        y_name = y_name.replace('.npy', '_c2.npy')
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print >> sys.stderr, "- data loading time:", data_loading_time
    print >> sys.stderr, "- benchmark gradient boost with", args.ns, "samples,", args.nf, "features..." 
    clf = ensemble.GradientBoostingClassifier(
        loss=args.loss,
        criterion=args.criterion,
        presort=args.presort
    )
    start_time = time()
    for _ in range(1):
        clf.fit(X, y)
    fit_time = time() - start_time
    print >> sys.stderr, "- benchmark finished, fitting time:", fit_time
