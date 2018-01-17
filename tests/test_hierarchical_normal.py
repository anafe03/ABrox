from scipy import stats
import numpy as np
from itertools import combinations

from abrox.core.abc import Abc

def summary(data):
    mean = np.mean(data)
    variance = np.var(data)
    mad = np.median(np.absolute(data - np.median(data)))
    raw = np.array([mean,variance,mad])
    all2sum = np.array([np.sum(tup) for tup in combinations(raw, 2)])
    all2prod = np.array([np.prod(tup) for tup in combinations(raw, 2)])
    all3sum = np.reshape(np.sum(raw),1)
    all3prod = np.reshape(np.prod(raw),1)
    return np.concatenate((raw,all2sum,all2prod,all3sum,all3prod))


def simulate_Model1(params):
    n = 100
    return np.random.normal(params['mu'],params['sigma'],size=n)


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
            "name": "Model1",
            "priors": [
                {"mu": {"dist": stats.norm, 'params': {'loc': 0, 'scale': 'sigma'}}},
                {"sigma": {"dist": stats.invgamma, 'params': {'a': 4, 'scale': 3}}}
        ],
        "simulate": simulate_Model1
        }

    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
        'method': {'algorithm': 'nn',
                   'specs': {}},
        'objective': 'inference',
        'outputdir': '.',
        'reftable': {'extref': None, 'simulations': int(10e4)},
        'test': {'fixed': {'mu': 4, 'sigma': 1}, 'model': 0}
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    out = abc.run()
    print(out)