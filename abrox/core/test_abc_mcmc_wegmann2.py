from scipy import stats
import numpy as np

from abrox.core.abc import Abc


def summary(data):
    """
    mean, variance, skew, kurtosis
    """
    # list(stats.describe(data))[2:]
    Mean = np.mean(data)
    Sd = np.std(data)
    return np.array([Mean,Sd])


def simulate_Model1(params):
    n = 1000
    return np.random.normal(params['mean'],params['sd'],size=n)


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
        "name": "Model1",
        "priors": [
            {'mean': stats.norm(loc=0.0, scale=5)},
            {'sd': stats.uniform(loc=0.0001,scale=10)}
        ],
        "simulate": simulate_Model1
        }

    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
        'method': {'algorithm': 'mcmc',
                   'specs': {'burn': 500,
                             'chl': 10000,
                             'keep': 100,
                             'proposal': None,
                             'start': None,
                             'thin': 1,
                             'threshold': None}},
        'objective': 'inference',
        'outputdir': '/Users/ulf.mertens/Desktop/abrox_demo/t_test',
        'reftable': {'extref': None, 'simulations': 10000},
        'test': {'fixed': {'mean': 3, 'sd': 2}, 'model': 0}
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    out = abc.run()
    print(out)