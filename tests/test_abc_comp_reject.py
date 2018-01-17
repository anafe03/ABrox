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
            "priors": [
                {"d": {"dist": stats.cauchy, 'params': {'loc': 0, 'scale': 0.7}}},
        ],
            "simulate": simulate_Model1
        },
        {
            "name": "Model2",
            "priors": [
            ],
            "simulate": simulate_Model2
        }

    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
        'method': {'algorithm': 'rejection',
                   'specs': {'cv': None, 'keep': 100, 'threshold': None}},
        'objective': 'comparison',
        'outputdir': '.',
        'reftable': {'extref': None, 'simulations': 10000},
        'test': {'fixed': {'d': 0.5}, 'model': 0}
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    out = abc.run()
    print(out)
