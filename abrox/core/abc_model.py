from collections import OrderedDict
import sys

class ABCModel:
    """Defines a model in a format suitable for ABC."""

    def __init__(self, name, priors, simulate):
        """
        Constructor requires following information:
        :param name: string - the internal name of the model
        :param prior: list - a list of dicts containing {priorName: stats.[dist]}
        :param simulate: function - the simulate function defined by the user
        """
        self.name = name
        self.currentParam = OrderedDict()
        self._priors = priors
        self._simulateFunc = simulate

    def drawParameter(self):
        """Draw a value from each prior distribution"""
        for priorDict in self._priors:
            for name, dist in priorDict.items():
                self.currentParam[name] = dist.rvs()
        return self.currentParam

    def getPriors(self):
        """Returns the list with model priors."""

        return self._priors

    def simulate(self, param):
        """
        Simulate data from user-defined simulate function.
        :param param: a dictionary with parameter-names : parameter-values
        :return: the output ot the simulate function
        """
        return self._simulateFunc(param)

    def __repr__(self):
        """Provides a nice representation of the user defined model."""

        return 'Model:(name={}, params={})'.format(
            self.name, [list(prior.keys())[0] for prior in self._priors])
