"""
Benchmark Random Forest
"""

from util import *
import numpy as np
import argparse
from time import time
from sklearn import ensemble
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark random forest.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--criterion', default='gini', type=str,
                        help="parameter for underlying random forest.")
    parser.add_argument('--bootstrap', default=True, type=str2bool,
                        help="parameter for underlying random forest.")
    parser.add_argument('--oob_score', default=False, type=str2bool,
                        help="parameter for underlying random forest.")
    args = parser.parse_args()

    print >> sys.stderr, "- loading data..."
    start_time = time()
    X_name = "dataset/cl3X_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/cl3y_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print >> sys.stderr, "- data loading time:", data_loading_time
    print >> sys.stderr, "- benchmark random forest with", args.ns, "samples,", args.nf, "features..." 
    clf = ensemble.RandomForestClassifier(
        n_estimators=100,
        criterion=args.criterion,
        bootstrap=args.bootstrap,
        oob_score=args.oob_score
    )
    start_time = time()
    for _ in range(1):
        clf.fit(X, y)
    fit_time = time() - start_time
    print >> sys.stderr, "- benchmark finished, fitting time:", fit_time
