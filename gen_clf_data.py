"""
Benchmark Linear Regression

"""
import numpy as np
import argparse
from time import time
from sklearn.datasets.samples_generator import make_classification

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark ordinary linear regression.")
    parser.add_argument('-ns', default=100, type=int,
                        help="Number of samples to be generated and fit.")
    parser.add_argument('-nf', default=20, type=int,
                        help="Number of features to be generated and fit.")
    parser.add_argument('--n_informative', default=2, type=int,
                        help="Defines how many features are informative.")
    parser.add_argument('--n_redundant', default=2, type=int,
                        help="Number of redundant features.")
    parser.add_argument('--n_repeated', default=0, type=int,
                        help="Number of duplicated features.")
    parser.add_argument('--n_classes', default=2, type=int,
                        help="Number of classes.")
    parser.add_argument('--n_clusters_per_class', default=2, type=int,
                        help="Number of clusters per class.")
    args = parser.parse_args()

    print "- generating data..."
    start_time = time()
    X, y = make_classification(n_samples=args.ns,
        n_features=args.nf, n_informative=args.n_informative,
        n_redundant=args.n_redundant, n_repeated=args.n_repeated,
        n_classes=args.n_classes, n_clusters_per_class=args.n_clusters_per_class
    )
    data_gen_time = time() - start_time
    print "- data generation time:", data_gen_time

    regX_name = "dataset/clfX_ns"+str(args.ns)+"_nf"+str(args.nf)+"_c"+str(args.n_classes)
    np.save(regX_name, X)
    regy_name = "dataset/clfy_ns"+str(args.ns)+"_nf"+str(args.nf)+"_c"+str(args.n_classes)
    np.save(regy_name, y)

    newX = np.load(regX_name+".npy")
    newy = np.load(regy_name+".npy")

    if (np.array_equal(newX, X) and np.array_equal(newy, y)):
        print "data verification pass"
    else:
        print "mismatch found in generated data"
