"""
This is an automatically generated script by ABrox GUI.
Created on 2017-12-21 19:11:12.011900.
"""

# Required imports
import numpy as np
from scipy import stats
from abrox.core.abc import Abc


def summary(data):
    v1, v2 = data[:,0], data[:,1]
    trans_v1, trans_v2 = np.abs(v1 - np.mean(v1)), np.abs(v2 - np.mean(v2))
    diff_means = np.mean(trans_v1) - np.mean(trans_v2)
    return diff_means


def simulate_H1(params):
    n2 = 100 // 2
    v1 = np.random.normal(0, 1, n2)
    v2 = np.random.normal(0, params['sigma'], n2)
    return np.column_stack((v1,v2))


def simulate_H0(params):
    n2 = 100 // 2
    v1 = np.random.normal(0, 1, n2)
    v2 = np.random.normal(0, 1, n2)
    return np.column_stack((v1,v2))


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
        "name": "H1",
        "priors": [
            {"sigma": stats.gamma(a=8.0, loc=0.0, scale=0.12)},
        ],
        "simulate": simulate_H1
        },
        {
        "name": "H0",
        "priors": [
        ],
        "simulate": simulate_H0
        },
    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
         'method': {'algorithm': 'rejection',
                    'specs': {'cv': None, 'keep': 100, 'threshold': None}},
         'objective': 'comparison',
         'outputdir': 'C:/Users/Developer/Desktop/Projects/git_abrox',
         'reftable': {'extref': None, 'simulations': 10000},
         'test': {'fixed': {'sigma': 1.3}, 'model': 0}
    }
}


if __name__ == "__main__":
    # Create and run an Abc instance
    abc = Abc(config=CONFIG)
    abc.run()
