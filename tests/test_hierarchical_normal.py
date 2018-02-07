from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from abrox.core.abc import Abc

from keras.models import load_model
from abrox.core.abc_utils import plotLosses


def summary(data):
    mean = np.mean(data)
    variance = np.var(data)
    mad = np.median(np.absolute(data - np.median(data)))
    raw = np.array([mean,variance,mad])
    all2sum = np.array([np.sum(tup) for tup in combinations(raw, 2)])
    all2prod = np.array([np.prod(tup) for tup in combinations(raw, 2)])
    all3sum = np.reshape(np.sum(raw),1)
    all3prod = np.reshape(np.prod(raw),1)
    noise = np.random.uniform(size=50)
    return np.concatenate((raw,all2sum,all2prod,all3sum,all3prod,noise))
    # return np.sort(data)


def simulate_Model1(params):
    n = 100
    return np.random.normal(params['mu'],np.sqrt(params['sigma']),size=n)


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
                   'specs': {'hidden_layers': 3,
                             'hidden_layer_sizes': [0.8,0.6,0.4],
                             'activation': 'relu',
                             'bn': False,
                             'loss': 'mean_squared_error',
                             'optimizer': 'adam',
                             'epochs': 10,
                             'val_size': 0.05,
                             'load_model': None}},
        'objective': 'inference',
        'outputdir': '/Users/ulf.mertens/Desktop/nndl/',
        'reftable': {'extref': None, 'simulations': int(10e4)},
        'test': {'fixed': {'mu': 0, 'sigma': 1}, 'model': 0}
    }
}


def samplesFromTruePosterior(data):
    """ Draw samples from true posterior distribution"""
    rawMean = data.mean()
    s2 = np.sum((data - rawMean) ** 2)
    N = len(data)
    print("N: ", N)
    truePosteriorMean = stats.t(df=N + 8, loc=(N * rawMean) / (N + 1), scale=(s2 + 6) / ((N + 1) * (N + 8)))
    truePosteriorVariance = stats.invgamma(a=54, scale=(N / 2) * (s2 / N) + 3)

    m = truePosteriorMean.mean() #truePosteriorMean.rvs(size=10000)
    mv = truePosteriorMean.var()
    v = truePosteriorVariance.mean() #truePosteriorVariance.rvs(size=10000)
    vv = truePosteriorVariance.var()

    return m, mv, v, vv


if __name__ == "__main__":

    # keras_model = load_model('/Users/ulf.mertens/Desktop/nndl/my_model.h5')

    abc = Abc(CONFIG)
    raw, loss, val_loss, ps = abc.run()

    PATH = '/Users/ulf.mertens/Desktop/nndl/'

    # sim = 100
    #
    # final = np.empty(shape=(sim,8))
    #
    # keras_model = load_model('/Users/ulf.mertens/Desktop/nndl/my_model.h5')
    #
    # for i in range(sim):
    #     CONFIG['settings']['test']['fixed']['sigma'] = stats.invgamma(a=4,scale=3).rvs()
    #     CONFIG['settings']['test']['fixed']['mu'] = stats.norm(loc=0,scale=CONFIG['settings']['test']['fixed']['sigma']).rvs()
    #
    #     abc = Abc(CONFIG)
    #     raw, loss,val_loss, ps = abc.run(keras_model)
    #
    #     #plotLosses(loss,val_loss,PATH)
    #
    #     expMean, expMeanVar, expVar, expVarVar = samplesFromTruePosterior(raw)
    #
    #     print("Running simulation {}/{}".format(i+1,sim))
    #
    #     final[i,0] = expMean #raw.mean()
    #     final[i,1] = ps[:,0].mean()
    #     final[i,2] = expVar #raw.var()
    #     final[i,3] = ps[:,1].mean()
    #     final[i,4] = expMeanVar
    #     final[i,5] = ps[:,0].var()
    #     final[i,6] = expVarVar
    #     final[i,7] = ps[:, 1].var()

    plotLosses(loss, val_loss, PATH)

    expMean, expMeanVar, expVar, expVarVar = samplesFromTruePosterior(raw)

    print("actual mean: ", raw.mean())
    print("actual var: ", raw.var())

    print("True var mean: ", np.array(expMeanVar))
    print("Est. var mean: ", ps[:,0].var)

    plt.hist(ps[:,0])
    plt.axvline(expMean, color='b', linestyle='dashed', linewidth=2)
    plt.savefig(PATH + 'mean.png', bbox_inches='tight')
    plt.clf()

    # VAR hist

    plt.hist(ps[:, 1])
    plt.axvline(expVar, color='b', linestyle='dashed', linewidth=2)
    plt.savefig(PATH + 'sigma.png', bbox_inches='tight')
    plt.clf()

    #np.savetxt(PATH + 'results.csv',final)