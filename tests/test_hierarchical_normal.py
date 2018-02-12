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
    n = 10
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
    truePosteriorVariance = stats.invgamma(a=(N/2)+4, scale=(N / 2) * (s2 / N) + 3)

    m = truePosteriorMean.mean() #truePosteriorMean.rvs(size=10000)
    mv = truePosteriorMean.var()
    v = truePosteriorVariance.mean() #truePosteriorVariance.rvs(size=10000)
    vv = truePosteriorVariance.var()

    return m, mv, v, vv


if __name__ == "__main__":

    # keras_model = load_model('/Users/ulf.mertens/Desktop/nndl/my_model.h5')

    #abc = Abc(CONFIG)
    #raw, loss, val_loss, relevant = abc.run()

    PATH = '/Users/ulf.mertens/Desktop/nndl/'

    sim = 100

    final = np.empty(shape=(sim,12))

    for i in range(sim):
        CONFIG['settings']['test']['fixed']['sigma'] = stats.invgamma(a=4,scale=3).rvs()
        CONFIG['settings']['test']['fixed']['mu'] = stats.norm(loc=0,scale=CONFIG['settings']['test']['fixed']['sigma']).rvs()

        abc = Abc(CONFIG)
        raw, loss, val_loss, relevant = abc.run()

        m1, m2, epi1, epi2, al1, al2 = relevant

        #plotLosses(loss,val_loss,PATH)

        expMean, expMeanVar, expVar, expVarVar = samplesFromTruePosterior(raw)

        print("Running simulation {}/{}".format(i+1,sim))

        final[i,0] = expMean #raw.mean()
        final[i,1] = m1
        final[i,2] = expVar #raw.var()
        final[i,3] = epi1 + al1
        final[i,4] = expMeanVar
        final[i,5] = m2
        final[i,6] = expVarVar
        final[i,7] = epi2 + al2
        final[i,8] = epi1
        final[i,9] = al1
        final[i,10] = epi2
        final[i,11] = al2

    # plotLosses(loss, val_loss, PATH)
    #
    # expMean, expMeanVar, expVar, expVarVar = samplesFromTruePosterior(raw)
    #
    # m1, m2, epi1, epi2, al1, al2 = relevant
    #
    # var1 = epi1 + al1
    # var2 = epi2 + al2
    #
    # posteriorMean = np.random.normal(loc=m1,scale=np.sqrt(var1),size=1000)
    # plt.hist(posteriorMean)
    # plt.axvline(expMean, color='b', linestyle='dashed', linewidth=2)
    # plt.savefig(PATH + 'mean.png', bbox_inches='tight')
    # plt.clf()
    #
    # # VAR hist
    # posteriorVariance = np.random.normal(loc=m2, scale=np.sqrt(var2), size=1000)
    # plt.hist(posteriorVariance)
    # plt.axvline(expVar, color='b', linestyle='dashed', linewidth=2)
    # plt.savefig(PATH + 'sigma.png', bbox_inches='tight')
    # plt.clf()

    np.savetxt(PATH + 'results.csv', final)