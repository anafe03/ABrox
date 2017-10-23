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
        self.preprocess = preprocess
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
        samples = np.empty(shape=(self.chainLength, len(start)))

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

        accepted = euclideanDistance(self.preprocess.scaledSumStatObsData,scaledSumStat,axis=0) < self.threshold
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


if __name__ == "__main__":

    pass
