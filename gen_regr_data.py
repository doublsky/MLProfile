"""
Benchmark Linear Regression

"""
import numpy as np
import argparse
from time import time
from sklearn.datasets.samples_generator import make_regression

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark ordinary linear regression.")
    parser.add_argument('-ns', default=1000000, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=100, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--informative_ratio', default=1.0, type=float,
                        help="Defines how many features are informative.")
    args = parser.parse_args()

    print "- generating data..."
    start_time = time()
    X, y = make_regression(n_samples=args.ns,
                           n_features=args.nf,
                           n_informative=int(args.nf * args.informative_ratio),
                           noise=0.1)
    data_gen_time = time() - start_time
    print "- data generation time:", data_gen_time

    regX_name = "dataset/regX_ns"+str(args.ns)+"_nf"+str(args.nf)
    np.save(regX_name, X)
    regy_name = "dataset/regy_ns"+str(args.ns)+"_nf"+str(args.nf)
    np.save(regy_name, y)

    newX = np.load(regX_name+".npy")
    newy = np.load(regy_name+".npy")

    if (np.array_equal(newX, X) and np.array_equal(newy, y)):
        print "data verification pass"
    else:
        print "mismatch found in generated data"
