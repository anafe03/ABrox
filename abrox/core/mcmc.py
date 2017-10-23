import numpy as np
from collections import Counter, OrderedDict
from scipy import stats
from abc_utils import euclideanDistance
from reference_table import AbcReferenceTable
from summary import Summary
from error_check import ConfigurationTester
from preparation import Prepare
from scale import Scaler
from preprocess import AbcPreprocesser
from plot import plotPosterior


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

    errorCheck = ConfigurationTester(CONFIG)

    if errorCheck.configTestPassed():

        prepare = Prepare(CONFIG)

        modelList = prepare.buildModels()
        simulations, keep, objective, nModels, parameterNames = prepare.getMetaInfo()
        obsData = prepare.getObservedData(modelList)
        summaryInstance = Summary(summary)
        sumStatObsData = summaryInstance.summarize(obsData)
        refTable = AbcReferenceTable()
        scaler = Scaler()
        preprocesser = AbcPreprocesser(modelList, summaryInstance, refTable, scaler)
        table = preprocesser.preprocess(sumStatObsData, simulations, parallel=False, jobs=4)

