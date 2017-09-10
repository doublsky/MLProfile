"""
Benchmark Logistic

"""
import numpy as np
import argparse
from time import time
from sklearn import linear_model

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark logistic regression.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--penalty', default='l2', type=str,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--dual', default=False, type=bool,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--tol', default=1e-4, type=float,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('-C', default=1.0, type=float,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--fit_intercept', default=True, type=bool,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--intercept_scaling', default=1, type=float,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--class_weight', default=None, type=str,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--solver', default='liblinear', type=str,
                        help="parameter for underlying logistic regression.")
    parser.add_argument('--multi_class', default='ovr', type=str,
                        help="parameter for underlying logistic regression.")
    args = parser.parse_args()

    print "- loading data..."
    start_time = time()
    X_name = "dataset/clfX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/clfy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print "- data loading time:", data_loading_time
    print "- benchmark logistic regression with", args.ns, "samples,", args.nf, "features"
    regr = linear_model.LogisticRegression(penalty=args.penalty, dual=args.dual,
        tol=args.tol, C=args.C, fit_intercept=args.fit_intercept, 
        intercept_scaling=args.intercept_scaling,
        class_weight=args.class_weight, solver=args.solver,
        multi_class=args.multi_class
    )
    start_time = time()
    regr.fit(X, y)
    fit_time = time() - start_time
    print "- benchmark finished, fitting time:", fit_time
    with open("bench_logistic.time", 'w') as f:
        f.write(str(fit_time)+'\n')
