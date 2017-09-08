"""
Benchmark Ridge

"""
import numpy as np
import argparse
from time import time
from sklearn import linear_model

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark ridge regression.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--alpha', default=1.0, type=float,
                        help="parameter for underlying ridge regression.")
    parser.add_argument('--fit_intercept', default=True, type=bool,
                        help="parameter for underlying ridge regression.")
    parser.add_argument('--normalize', default=False, type=bool,
                        help="parameter for underlying ridge regression.")
    parser.add_argument('--solver', default='auto', type=str,
                        help="parameter for underlying ridge regression.")
    args = parser.parse_args()

    print "- generating data..."
    start_time = time()
    X_name = "dataset/regX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/regy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print "- data loading time:", data_loading_time
    print "- benchmark ridge regression..." 
    regr = linear_model.Ridge(copy_X=False, alpha=args.alpha, normalize=args.normalize, fit_intercept=args.fit_intercept, solver=args.solver)
    tstart = time()
    regr.fit(X, y)
    fit_time = time() - tstart
    print "- benchmark finished, fitting time:", fit_time, "sec"
    with open("bench_ridge.time", "w") as f:
        f.write(str(fit_time)+'\n')
