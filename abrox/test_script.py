"""
This is an automatically generated script by ABrox GUI.
Created on 2017-09-15 11:13:39.993596.
"""

# Required imports
import numpy as np
from scipy import stats
from abrox.core.algorithm import Abc


def summary(data):
    data_mean = np.mean(data, axis=0)
    diff_mean = data_mean[0] - data_mean[1]
    mean_std = np.mean(np.std(data,axis=0))
    return diff_mean / mean_std
    


def simulate_Model1(params):
    n = 50
    first_sample = np.random.normal(0,1,n)
    sec_sample = np.random.normal(params['d'],1,n)
    return np.column_stack((first_sample,sec_sample))


def simulate_Model2(params):
    n = 50
    first_sample = np.random.normal(0,1,n)
    sec_sample = np.random.normal(0,1,n)
    return np.column_stack((first_sample,sec_sample))


CONFIG = {
    "data": {
        "datafile": "None",
        "delimiter": "None"
    },
    "models": [
        {
        "name": "Model1",
        "priors": [
            {"d": stats.cauchy(loc=0.0, scale=0.7)},
        ],
        "simulate": simulate_Model1
        },
        {
        "name": "Model2",
        "priors": [
        ],
        "simulate": simulate_Model2
        },
    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
         'fixedparameters': {'d': 0.1},
         'method': 'logistic',
         'modeltest': 0,
         'objective': 'comparison',
         'outputdir': 'C:/Users/Developer/Desktop/Projects/ApproxBayes/test_scripts',
         'particles': 1000.0,
         'percentile': 0.05,
         'threshold': -1
    }
}


if __name__ == "__main__":
    # Create and run an Abc instance
    abc = Abc(config=CONFIG)
    abc.run()
