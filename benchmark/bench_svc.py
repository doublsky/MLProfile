"""
Benchmark SVC

"""
import numpy as np
import argparse
from time import time
from sklearn import svm
import sys

def str2bool(t):
    if (t == 'True'):
        return True
    elif (t == 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark SVC.")
    parser.add_argument('-ns', default=10000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--kernel', default='rbf', type=str,
                        help="parameter for underlying svm.")
    parser.add_argument('--degree', default=3, type=int,
                        help="parameter for underlying svm.")
    parser.add_argument('--probability', default=False, type=str2bool,
                        help="parameter for underlying svm.")
    parser.add_argument('--shrinking', default=True, type=str2bool,
                        help="parameter for underlying svm.")
    parser.add_argument('--decision_function_shape', default="ovr",
                        help="parameter for underlying svm.")
    args = parser.parse_args()

    print >> sys.stderr, "- loading data..."
    start_time = time()
    X_name = "dataset/clfX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/clfy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print >> sys.stderr, "- data loading time:", data_loading_time
    print >> sys.stderr, "- benchmark SVC with", args.ns, "samples,", args.nf, "features"
    clf = svm.SVC(
        kernel=args.kernel,
        degree=args.degree,
        probability=args.probability,
        shrinking=args.shrinking,
        decision_function_shape=args.decision_function_shape
    )
    start_time = time()
    clf.fit(X, y)
    fit_time = time() - start_time
    print >> sys.stderr, "- benchmark finished, fitting time:", fit_time
