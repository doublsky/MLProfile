"""
Benchmark Multi-Level Perceptron
"""

from util import *
import numpy as np
import argparse
from time import time
from sklearn import neural_network
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark MLP.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--activation', default='relu', type=str,
                        help="parameter for underlying MLP.")
    parser.add_argument('--solver', default='adam', type=str,
                        help="parameter for underlying MLP.")
    parser.add_argument('--batch_size', default=200, type=int,
                        help="parameter for underlying MLP.")
    parser.add_argument('--learning_rate', default='constant', type=str,
                        help="parameter for underlying MLP.")
    parser.add_argument('--nesterovs_momentum', default=True, type=str2bool,
                        help="parameter for underlying MLP.")
    args = parser.parse_args()

    print >> sys.stderr, "- loading data..."
    start_time = time()
    X_name = "dataset/cl3X_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/cl3y_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print >> sys.stderr, "- data loading time:", data_loading_time
    print >> sys.stderr, "- benchmark MLP with", args.ns, "samples,", args.nf, "features..." 
    clf = neural_network.MLPClassifier(
        activation=args.activation,
        solver=args.solver,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        nesterovs_momentum=args.nesterovs_momentum
    )
    start_time = time()
    for _ in range(10):
        clf.fit(X, y)
    fit_time = time() - start_time
    print >> sys.stderr, "- benchmark finished, fitting time:", fit_time
