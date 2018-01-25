from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
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
    noise = np.random.uniform(size=50)
    return np.concatenate((raw,all2sum,all2prod,all3sum,all3prod,noise))
    # return data


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
                   'specs': {}},
        'objective': 'inference',
        'outputdir': '.',
        'reftable': {'extref': None, 'simulations': int(10e4)},
        'test': {'fixed': {'mu': 0, 'sigma': 1}, 'model': 0}
    }
}


if __name__ == "__main__":

    abc = Abc(CONFIG)
    raw, loss,val_loss, ps = abc.run()

    epochs = range(1,len(loss)+1)
    plt.plot(epochs,loss,'bo',label="Training loss")
    plt.plot(epochs, val_loss, 'b', label="Validation loss")
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig('/Users/ulf.mertens/Desktop/nndl/losses.png', bbox_inches='tight')
    plt.clf()

    rawMean = raw.mean()
    s2 = np.sum((raw - rawMean) ** 2)
    s = np.sum(raw - rawMean)
    N = 100
    truePosteriorMean = stats.t(df=N + 8, loc=(N*raw.mean())/(N+1), scale=(s2 + 6) / ((N + 1) * (N + 8)))
    samplesPostMean = truePosteriorMean.rvs(size=10000)
    plt.hist(samplesPostMean,normed=True)
    truePosteriorVariance = stats.invgamma(a=54, scale=(N / 2) * (s2 / N) + 3)
    samplesPostVar = truePosteriorVariance.rvs(size=10000)

    #plt.plot(xsd, fitSD, '-')
    plt.hist(ps[:,0],normed=True)
    plt.savefig('/Users/ulf.mertens/Desktop/nndl/mean.png', bbox_inches='tight')
    plt.clf()

    plt.hist(samplesPostVar,normed=True)
    plt.hist(ps[:, 1], normed=True)
    plt.savefig('/Users/ulf.mertens/Desktop/nndl/sigma.png', bbox_inches='tight')
    plt.clf()

    print("True mean: ", stats.describe(samplesPostMean))
    print("True sd: ", stats.describe(samplesPostVar))

    print("Est mean: ",stats.describe(ps[:,0]))
    print("Est sd: ",stats.describe(ps[:,1]))
    #plt.xlim(0,2)


    #plt.hist(ps[:,1])
    #plt.show()