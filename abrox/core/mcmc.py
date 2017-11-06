import numpy as np
from abrox.core.abc_utils import euclideanDistance


class MCMC:

    def __init__(self, preprocess, paramNames, proposal, threshold):
        self.summary = preprocess.summarizer
        self.model = preprocess._getFirstModel()
        self.scaler = preprocess.scaler
        self.preprocess = preprocess
        self.proposal = proposal
        self.paramNames = paramNames
        self.prior = self.model.prior
        self.threshold = threshold

    def metropolis(self, old):
        """basic metropolis algorithm"""
        new = old + self.makeProposal()
        accProb = np.min([self.density(new) / self.density(old), 1])
        u = np.random.uniform()

        cnt = 0
        if self.checkDistance(new) and u < accProb:
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

    def run(self, start, chainLength=10000, burn=0, thin=1):
        """
        Start MCMC sampling.
        :param start: starting value
        :param chainLength: length of chain
        :param burn: burn-in
        :param thin: thinning
        :return: the accepted samples
        """
        accepted = 0
        samples = np.empty(shape=(chainLength, len(start)))

        samples[0,:] = start

        for i in range(chainLength-1):
            start, accept = self.metropolis(start)
            accepted += accept
            if i % thin is 0:
                samples[i+1,:] = start

        return samples[burn:,:], accepted

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
