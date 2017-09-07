######################################
# ABC t-Test
######################################

import numpy as np
from scipy import stats
from algorithm import Abc
# from basemodel import Model


def summary(data):
    v1, v2 = data[0], data[1]
    diff_means = np.mean(v2) - np.mean(v1)
    overall_std = (np.std(v1) + np.std(v2)) / 2
    return diff_means / overall_std


def simulate(param):
    n2 = 100 // 2
    v1 = np.random.normal(0, 1, n2)
    v2 = np.random.normal(param["d"], 1, n2)
    return np.array([v1, v2])


t_test = {
    "data": {
        "datafile": "data/test.csv"
    },
    "models": [
        {
            "name": "Nullmodel",
            "priors": [{"d": 0}],
            "simulate": simulate
        },
        {
            "name": "AltModel",
            "priors": [{"d": stats.cauchy(scale=0.707)}],
            "simulate": simulate
        }
    ],
    "summary": summary,
    "distance": "",
    "settings": {
        "distance_metric": "default",
        "outputdir": ".",
        "particles": 1000,
        "threshold": -1,
        "percentile": 0.05,
        "modeltest": "AltModel",
        "objective": "comparison",
        "method": "logistic",
        "fixedparameters": {"d": 0.3}
    }
}


python - m pip install pandas


# SETTINGS
NPARTICLE = int(1e5)
THRESHOLD = []
PERCENTILE = 0.01
JOBS = 1


# MODEL SETTINGS
# altmodel = Model(name="Alternative Model")
# altmodel.prior = {"d": stats.cauchy(scale=0.707)}
# altmodel.distance_metric = "euclidean"
# altmodel.simulate = simulate
# altmodel.summary = summary


# MODEL SETTINGS
# nullmodel = Model(name="Null Model")
# nullmodel.prior = {"d": 0}
# nullmodel.distance_metric = "euclidean"
# nullmodel.simulate = simulate
# nullmodel.summary = summary


# save models (model comparison)
# models = [altmodel, nullmodel]

# save model (parameter estimation)
# models = [altmodel]

# generate data from altmodel
# data = altmodel.simulate({"d": 0.3})


def main():
    # abc = Abc(nparticle=NPARTICLE,
    #               threshold=THRESHOLD,
    #               models=models,
    #               objective="comparison",
    #               method="logistic",
    #               jobs=JOBS,
    #               percentile=PERCENTILE)
    #
    # abc.run(data)
    abc = Abc(configFile=t_test)
    abc.run()


if __name__ == '__main__':
    main()
