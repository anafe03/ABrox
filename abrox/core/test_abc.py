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
        }

    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
         'fixedparameters': {'d': 0.5},
         'method': 'mcmc',
         'type': 'wegmann',
         'modeltest': 0,
         'objective': 'inference',
         'outputdir': '/Users/ulf.mertens/Desktop/abrox_demo/t_test',
         'simulations': 10000,
         'keep': 100,
         'threshold': -1
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    out = abc.run()
    print(len(out))
    # TODO:
    # Sampling parameters is currently not really fast since the prior
    # distributions are the values from dicts in lists.
    # The draw_Parameter method in Model class needs to access these
    # values every time. I am not sure how this slows down the whole process.