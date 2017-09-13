"""
This is an automatically generated script by ABrox GUI.
Created on 2017-09-11 14:32:55.149241.
"""

# Required imports
import numpy as np
from scipy import stats
from abrox.core.algorithm import Abc


def summary(params):
    # write your code here
    pass


def simulate_Model1(params):
    # write your code here
    pass


CONFIG = {
    "data": {
        "datafile": "None"
    },
    "models": [
        {
            "name": "Model1",
            "priors": [
                {"a": stats.norm(loc=0.0, scale=1.0)},
            ],
            "simulate": simulate_Model1
        },
    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
        'fixedparameters': [],
        'method': 'rejection',
        'modeltest': False,
        'objective': 'inference',
        'particles': 1000,
        'percentile': 0.05,
        'threshold': 0.0
    }
}


if __name__ == "__main__":
    # Create and run an Abc instance
    abc = Abc(config=CONFIG)
    abc.run()
