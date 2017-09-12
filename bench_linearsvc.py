"""
Benchmark linear SVC

"""
import numpy as np
import argparse
from time import time
from sklearn import svm

def str2bool(t):
    if (t == 'True'):
        return True
    elif (t == 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark linear SVC.")
    parser.add_argument('-ns', default=10000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--penalty', default='l2', type=str,
                        help="parameter for underlying svm.")
    parser.add_argument('--loss', default='squared_hinge', type=str,
                        help="parameter for underlying svm.")
    parser.add_argument('--dual', default=True, type=str2bool,
                        help="parameter for underlying svm.")
    parser.add_argument('--fit_intercept', default=True, type=bool,
                        help="parameter for underlying svm.")
    parser.add_argument('--intercept_scaling', default=1, type=float,
                        help="parameter for underlying svm.")
    parser.add_argument('--class_weight', default=None, type=str,
                        help="parameter for underlying svm.")
    parser.add_argument('--multi_class', default='ovr', type=str,
                        help="parameter for underlying svm.")
    args = parser.parse_args()

    print args.dual

    print "- loading data..."
    start_time = time()
    X_name = "dataset/clfX_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    X = np.load(X_name)
    y_name = "dataset/clfy_ns"+str(args.ns)+"_nf"+str(args.nf)+".npy"
    y = np.load(y_name)
    data_loading_time = time() - start_time
    print "- data loading time:", data_loading_time
    print "- benchmark linear SVC with", args.ns, "samples,", args.nf, "features"
    clf = svm.LinearSVC(
        penalty=args.penalty,
        loss=args.loss,
        dual=args.dual,
        fit_intercept=args.fit_intercept, 
        intercept_scaling=args.intercept_scaling,
        class_weight=args.class_weight,
        multi_class=args.multi_class
    )
    start_time = time()
    clf.fit(X, y)
    fit_time = time() - start_time
    print "- benchmark finished, fitting time:", fit_time
    with open("bench_linearsvc.time", 'w') as f:
        f.write(str(fit_time)+'\n')
