import numpy as np
from collections import OrderedDict
from scipy import stats

from abrox.core.abc_utils import toArray


class Wegmann:

    def __init__(self, subset, paramNames):
        self.paramArray = toArray(subset,'param')
        self.paramNames = paramNames

    def getProposal(self):
        """
        Return the standard deviation of each parameter column
        :param subset:
        :return: an array of standard deviations
        """

        standardDeviation = np.std(self.paramArray,axis=0)

        proposal = OrderedDict()
        for paramName, sd in zip(self.paramNames,standardDeviation):
            proposal[paramName] = stats.uniform(loc=-sd/10, scale=(sd/10)*2)

        return proposal

    def getStartingValues(self):
        """
        Pick a random row from the subset as starting values for Wegmann MCMC.
        :return: an array of shape (1,#parameter)
        """
        return self.paramArray[self._pickRandomRowIndex()]

    def _pickRandomRowIndex(self):
        """
        Pick a random row index from the subset reference table.
        :return: the index
        """
        return np.random.choice(self.paramArray.shape[0], 1, replace=False)[0]