import numpy as np
from collections import Counter, OrderedDict
from scipy import stats

from abrox.core.abc_utils import euclideanDistance
from abrox.core.reference_table import RefTable
from abrox.core.summary import Summary
from abrox.core.error_check import ErrorCheck
from abrox.core.preparation import Prepare
from abrox.core.scale import Scaler
from abrox.core.preprocess import Preprocess
from abrox.core.plot import plotPosterior


class MCMC:

    def __init__(self, preprocess, proposal, paramNames, threshold, chainLength):
        self.summary = preprocess.summarizer
        self.model = preprocess.getFirstModel()
        self.scaler = preprocess.scaler
        self.proposal = proposal
        self.paramNames = paramNames
        self.prior = self.model.prior
        self.threshold = threshold
        self.chainLength = chainLength

    def metropolis(self, old):
        """basic metropolis algorithm"""
        new = old + self.makeProposal()
        alpha = np.min([self.density(new) / self.density(old), 1])
        u = np.random.uniform()

        cnt = 0
        if self.checkDistance(new) and u < alpha:
            old = new
            cnt = 1

        return old, cnt

    def listToDict(self,paramList):
        """
        Convert a list of parameters to dictionary.
        Necessary since model.simulate() only accepts dict.
        :param paramList: list of parameters
        :return: the dictionary
        """
        return {k: v for k, v in zip(self.paramNames, paramList)}

    def run(self, start, take=1):
        """
        Start MCMC sampling.
        :param start: starting value
        :param n: length of chain
        :param take: thinning
        :return: the accepted samples
        """
        accepted = 0
        samples = np.empty(shape=(chainLength,len(start)))

        samples[0,:] = start

        for i in range(self.chainLength-1):
            start, accept = self.metropolis(start)
            accepted += accept
            if i % take is 0:
                samples[i+1,:] = start

        return samples, accepted

    def checkDistance(self,param):
        """
        Check if distance between simulated summary statistics
        and observed summary statistics is < threshold
        :param param: Sampled parameters
        :return: True if smaller than threshold False otherwise
        """

        param = self.listToDict(param)

        sumstat = self.summary.summarize(self.model.simulate(param))
        scaledSumStat = self.scaler.transform(sumstat)

        accepted = euclideanDistance(preprocess.scaledSumStatObsData,scaledSumStat,axis=0) < self.threshold
        return accepted

    def makeProposal(self):
        """
        Generate proposed values according to proposal distributions
        :return: Proposed values
        """
        proposedValue = []
        for paramName, proposal in self.proposal.items():
            proposedValue.append(proposal.rvs())
        return np.array(proposedValue)

    def uniformProposal(self, lower, upper):
        """
        Uniform proposal generating function
        :param lower: lowest value
        :param upper: highest value
        :return: scipy.stats object
        """
        return np.random.uniform(low=lower,high=lower+upper)

    def density(self,value):
        """
        Return overall density as sum of individual log densities
        :param value: the value(s) the density is evaluated on
        :return: the overall density
        """
        density = 0
        for prior in self.prior:
            for dist in prior.values():
                density += dist.logpdf(value)
        return density





def summary(data):
    data_mean = np.mean(data, axis=0)
    diff_mean = data_mean[0] - data_mean[1]
    mean_std = np.mean(np.std(data, axis=0))
    return diff_mean / mean_std

def simulate_Model1(params):
    n = 500
    first_sample = np.random.normal(0, 1, n)
    sec_sample = np.random.normal(params['d'], 1, n)
    return np.column_stack((first_sample, sec_sample))


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
        "name": "Model1",
        "prior": [
            {"d": stats.cauchy(loc=0.0, scale=0.7)},
        ],
        "simulate": simulate_Model1
        }
    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
         'fixedparameters': {'d': 0.5},
         'method': 'rejection',
         'modeltest': 0,
         'objective': 'inference',
         'outputdir': '/Users/ulf.mertens/Desktop/abrox_demo/t_test',
         'simulations': 10000,
         'keep': 100,
         'threshold': -1
    }
}


if __name__ == "__main__":

    errorCheck = ErrorCheck(CONFIG)
    errorCheck.run()

    prepare = Prepare(CONFIG)

    modelList = prepare.buildModel()

    simulations, keep, objective, paramNames = prepare.getMetaInfo()

    print("names: ", paramNames)

    obsData = prepare.getObservedData(modelList)

    summaryClass = Summary(summary)
    sumStatObsData = summaryClass.summarize(obsData)

    abcTable = RefTable()
    scaler = Scaler()

    preprocess = Preprocess(modelList, summaryClass, abcTable, scaler)

    preprocess.run(sumStatObsData,simulations, parallel=True, jobs=4)

    proposalDist = OrderedDict([("d", stats.uniform(-0.05, 0.1))])

    threshold = 0.05
    chainLength = 10000
    mcmc = MCMC(preprocess, proposalDist, paramNames, threshold, chainLength)
    samples, accepted = mcmc.run(np.array([0.3]))

    plotter = plotPosterior(samples, paramNames)
    # plotter.plot()

    print(accepted)
