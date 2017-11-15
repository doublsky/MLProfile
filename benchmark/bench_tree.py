"""
Benchmark Decision Tree
"""

from util import *
import numpy as np
import argparse
from time import time
from sklearn import tree

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark decision tree.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--criterion', default='gini', type=str,
                        help="parameter for underlying decision tree.")
    parser.add_argument('--splitter', default='best', type=str,
                        help="parameter for underlying decision tree.")
    parser.add_argument('--presort', default=False, type=str2bool,
                        help="parameter for underlying decision tree.")
    args = parser.parse_args()

    print "- loading data..."
    start_time = time()
    X_name = "dataset/clfX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/clfy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print "- data loading time:", data_loading_time
    print "- benchmark decision tree with", args.ns, "samples,", args.nf, "features..." 
    clf = tree.DecisionTreeClassifier(
        criterion=args.criterion,
        splitter=args.splitter,
        presort=args.presort
    )
    start_time = time()
    for _ in range(1):
        clf.fit(X, y)
    fit_time = time() - start_time
    print "- benchmark finished, fitting time:", fit_time
