import numpy as np
import pandas as pd

from abrox.core.abc_utils import euclideanDistance
from abrox.core.abc_wegmann import Wegmann


class MCMC:
    """
    Implements the MCMC sampling algorithm without likelihood.
    """
    #TODO - give reference to paper

    def __init__(self, preprocessor, subset, threshold, settings):

        self._pp = preprocessor
        self._subset = subset
        self._settings = settings
        self._settings['specs']['threshold'] = threshold
        self._model = self._pp.getFirstModel()
        self._priors = self._model.getPriors()

        if settings['specs']['proposal'] is None:
            self._initWegmann()

    def run(self):
        """Runs an ABC-MCMC sampling chain."""

        # Extract settings
        chainLength = self._settings['specs']['chl']
        thin = self._settings['specs']['thin']
        burn = self._settings['specs']['burn']
        start = self._settings['specs']['start']
        accepted = 0

        # Pre-initialize an array to hold samples
        samples = np.empty(shape=(chainLength, len(start)))
        samples[0, :] = start

        for i in range(chainLength-1):
            start, accept = self._metropolis(start)
            accepted += accept
            if i % thin is 0:
                samples[i+1, :] = start

        df = pd.DataFrame(samples[burn:, :], columns=self._settings['pnames'])

        df.to_csv(self._settings['outputdir'] + '/posteriorSamples_mcmc.csv')

        return df, df.describe(), accepted

    def _initWegmann(self):
        """
        Determines starting value of the chain and proposal distribution using
        the algorithm by Wegmann.
        :return: None
        """

        wegmann = Wegmann(self._subset, self._settings['pnames'])
        self._settings['specs']['proposal'] = wegmann.getProposal()
        self._settings['specs']['start'] = wegmann.getStartingValues()

    def _metropolis(self, old):
        """Implements a single step of the metropolis algorithm."""

        new = old + self._propose()
        accProb = np.min([self._density(new) / self._density(old), 1])
        u = np.random.uniform()

        cnt = 0
        if self._distance(new) and u < accProb:
            old = new
            cnt = 1

        return old, cnt

    def _distance(self, param):
        """
        Check if distance between simulated summary statistics
        and observed summary statistics is < threshold
        :param param: Sampled parameters
        :return: True if smaller than threshold False otherwise
        """

        # Get parameters in the desired form
        param = self._listToDict(param)

        # Simulate dataset, compute summary, and scale it
        try:
            simulation = self._model.simulate(param)
        except ValueError:
            return False

        sumStat = self._pp.summarizer.summarize(simulation)
        scaledSumStat = self._pp.scaler.transform(sumStat)

        # Decide whether to accept sample or not
        dist = euclideanDistance(self._pp.scaledSumStatObsData, scaledSumStat, axis=0)
        accepted = dist < self._settings['specs']['threshold']
        return accepted

    def _density(self, value):
        """
        Return overall density as sum of individual log densities
        :param value: the value(s) the density is evaluated on
        :return: the overall density
        """

        density = 0
        for prior in self._priors:
            for i, dist in enumerate(prior.values()):
                density += dist.logpdf(value[i])
        return density

    def _propose(self):
        """
        Generate proposed values according to proposal distributions
        :return: Proposed values
        """

        proposedValue = []
        for paramName, proposal in self._settings['specs']['proposal'].items():
            proposedValue.append(proposal.rvs())
        return np.array(proposedValue)

    def _listToDict(self, paramList):
        """
        Convert a list of parameters to a dictionary.
        Necessary since model.simulate() only accepts dict.
        :param paramList: list of parameters
        :return: the created dictionary
        """

        return {k: v for k, v in zip(self._settings['pnames'], paramList)}
