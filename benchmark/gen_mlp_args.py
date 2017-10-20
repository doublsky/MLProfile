"""
Generate argument list for benchmark MLP
"""

from sklearn.model_selection import ParameterGrid

def dict_to_str(input_dict):
    return ' '.join('{} {}'.format(key, val) for key, val in input_dict.items())

arg_dict = {
    "--activation": ['logistic', 'tanh', 'relu'],
    "--solver": ['lbfgs', 'sgd', 'adam'],
    "--learning_rate": ['constant', 'invscaling', 'adaptive'],
    "-ns": [10000, 100000, 1000000],
    "-nf": [100, 1000, 10000]
}
arg_grid = ParameterGrid(arg_dict)

with open('bench_mlp.args', 'w') as f:
    for arg in arg_grid:
        if (arg['-ns'] * arg['-nf'] <= 100000000):
            f.write(dict_to_str(arg)+"\n")
