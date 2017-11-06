from scipy import stats
import numpy as np

from abrox.core.abc import Abc

def summary(data):
    data_mean = np.mean(data, axis=0)
    diff_mean = data_mean[0] - data_mean[1]
    mean_std = np.mean(np.std(data, axis=0))
    return diff_mean / mean_std

def simulate_Model1(params):
    n = 1000
    first_sample = np.random.normal(0, 1, n)
    sec_sample = np.random.normal(params['d'], 1, n)
    return np.column_stack((first_sample, sec_sample))

def simulate_Model2(params):
    n = 1000
    first_sample = np.random.normal(0, 1, n)
    sec_sample = np.random.normal(0, 1, n)
    return np.column_stack((first_sample, sec_sample))


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
            "name": "Model1",
            "prior": [
                {"d": stats.cauchy(loc=0.0, scale=0.7)},
        ],
            "simulate": simulate_Model1
        },
        {
            "name": "Model2",
            "prior": [
                {},
            ],
            "simulate": simulate_Model2
        }

    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
        'objective': 'inference',
        'method': {'algorithm': 'rejection', 'specs':  {'proposal': None, 'start': None}},
        'test': {'model': 0, 'parameter': {'d': 0.2}},
        'preprocess': {'simulations': 1000,  'keep': 100, 'threshold': -1},
        'outputdir': '/Users/ulf.mertens/Desktop/abrox_demo/t_test'
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    out = abc.run()
    print(out)
