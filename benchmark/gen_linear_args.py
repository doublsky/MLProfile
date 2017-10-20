"""
Generate argument list for benchmark linear regression.
"""

from sklearn.model_selection import ParameterGrid

def dict_to_str(input_dict):
    return ' '.join('{} {}'.format(key, val) for key, val in input_dict.items())

arg_dict = {
    "-ns": [100, 1000],
    "-nf": [10, 100]
}
arg_grid = ParameterGrid(arg_dict)

with open('bench_linear.args', 'w') as f:
    for arg in arg_grid:
        if (arg['-ns'] * arg['-nf'] <= 100000000):
            f.write(dict_to_str(arg)+"\n")
