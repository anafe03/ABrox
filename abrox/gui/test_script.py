"""
This is an automatically generated script by ABrox GUI.
Created on 2017-09-11 09:42:19.464644.
"""

# Required imports
import numpy as np
from scipy import stats
from abrox.core.algorithm import Abc


def function():
    print('dsdsds')
    


def simulate_Model1(params):
    # write your code here
    print('I am model 1 function')



def simulate_Model2(params):
    # write your code here
    


CONFIG = {
    "data": {
        "datafile": "C:/Users/Developer/Desktop/Projects/ApproxBayes/test_data.csv"
    },
    "models": [
        {
        "name": "Model1",
        "priors": [
            {"dsds": stats.norm(loc=1.0, scale=1.0)},
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
         'fixedparameters': [],
         'method': 'logistic',
         'modeltest': False,
         'objective': 'comparison',
         'particles': 1000,
         'percentile': 0.05,
         'threshold': -1
    }
}


if __name__ == "__main__":
    # Create and run an Abc instance
    abc = Abc(config=CONFIG)
    abc.run()
