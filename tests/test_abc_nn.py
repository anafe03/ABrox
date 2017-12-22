from scipy import stats
import numpy as np
from abrox.core.abc import Abc


def summary(data):
    Mean = np.mean(data)
    Sd = np.std(data)
    return [Mean,Sd]


def simulate_Model1(params):
    n = 100
    return np.random.normal(params['mean'],params['sd'],size=n)


def simulate_Model2(params):
    n = 100
    return np.random.normal(params['mean'], 1, size=n)


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
            "name": "Model1",
            "prior": [
                {"mean": stats.norm(loc=0.0, scale=1), "sd": stats.uniform(0,5)},
        ],
            "simulate": simulate_Model1
        },
        {
            "name": "Model2",
            "prior": [
                {"mean": stats.norm(loc=0.0, scale=1)},
            ],
            "simulate": simulate_Model2
        }

    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
        'objective': 'comparison',
        'method': {'algorithm': 'nn', 'specs':  {}},
        'test': {'model': 0, 'parameter': {'mean': 0.5, 'sd': 1}},
        'preprocess': {'simulations': 10000,  'keep': 100, 'threshold': -1},
        'outputdir': '/Users/ulf.mertens/Desktop/abrox_demo/t_test'
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    out = abc.run()
    print("Predicted model probabilities: ", out)
