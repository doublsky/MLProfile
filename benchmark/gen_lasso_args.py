"""
Generate argument list for benchmark lasso regression.
"""

from sklearn.model_selection import ParameterGrid

def dict_to_str(input_dict):
    return ' '.join('{} {}'.format(key, val) for key, val in input_dict.items())

arg_dict = {
    "--fit_intercept": [True, False],
    "--normalize": [True, False],
    "--precompute": [True, False],
    "--positive": [True, False],
    "--selection": ['cyclic', 'random'],
    "-ns": [10000, 100000, 1000000],
    "-nf": [100, 1000, 10000]
}
arg_grid = ParameterGrid(arg_dict)

with open('bench_lasso.args', 'w') as f:
    for arg in arg_grid:
        if (arg['-ns'] * arg['-nf'] <= 100000000):
            f.write(dict_to_str(arg)+"\n")
