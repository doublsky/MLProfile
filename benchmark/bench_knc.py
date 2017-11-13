"""
Benchmark K Nearest Neighbor Classifier

"""
from util import *
import numpy as np
import argparse
from time import time
from sklearn import neighbors
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark K Nearest Neighbor Classifier.")
    parser.add_argument('-ns', default=10000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--n_neighbors', default=5, type=int,
                        help="parameter for underlying k nearest neighbors classifier.")
    parser.add_argument('--weights', default='uniform', type=str,
                        help="parameter for underlying k nearest neighbors classifier.")
    parser.add_argument('--algorithm', default='auto', type=str,
                        help="parameter for underlying k nearest neighbors classifier.")
    parser.add_argument('-p', default=2, type=int,
                        help="parameter for underlying k nearest neighbors classifier.")
    parser.add_argument('--metric', default='minkowski', type=str,
                        help="parameter for underlying k nearest neighbors classifier.")
    parser.add_argument('--metric_params', default=None, type=dict,
                        help="parameter for underlying k nearest neighbors classifier.")
    args = parser.parse_args()

    print >> sys.stderr, "- loading data..."
    start_time = time()
    X_name = "dataset/cl3X_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/cl3y_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print >> sys.stderr, "- data loading time:", data_loading_time
    print >> sys.stderr, "- benchmark K nearest neighbors classifier..." 
    clf = neighbors.KNeighborsClassifier(
        n_neighbors=args.n_neighbors,
        weights=args.weights,
        algorithm=args.algorithm,
        p=args.p,
        metric=args.metric,
        metric_params=args.metric_params
    )
    start_time = time()
    clf.fit(X, y)
    fit_time = time() - start_time
    print >> sys.stderr, "- benchmark finished, fitting time:", fit_time
