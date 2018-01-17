from collections import OrderedDict
import numpy as np

class ABCModel:
    """Defines a model in a format suitable for ABC."""

    def __init__(self, name, priors, simulate, n):
        """
        Constructor requires following information:
        :param name: string - the internal name of the model
        :param prior: list - a list of dicts containing {priorName: stats.[dist]}
        :param simulate: function - the simulate function defined by the user
        """
        self.name = name
        self._priorSet = OrderedDict()
        self._called = -1
        self._priors = priors
        self._simulateFunc = simulate
        self._priorSamples = self.draw(n)

    def draw(self, n):
        """
        Draw n prior samples and store in OrderedDict
        :param n: number of samples to draw
        :return: an ordered dict with keys corresponding to parameter names
        and values are np arrays containing the samples.
        """
        currentParam = OrderedDict()

        for priorDict in self._priors:

            for name, priorInfo in priorDict.items():
                if all(isinstance(val, (float, int)) for val in priorInfo['params'].values()):
                    currentParam[name] = priorInfo['dist'](**priorInfo['params']).rvs(size=n)
                else:
                    currentParam[name] = None

        for priorDict in self._priors:
            for name, priorInfo in priorDict.items():
                if currentParam[name] is None:
                    for paramName, val in priorInfo['params'].items():
                        if isinstance(val, str):
                            priorInfo['params'][paramName] = currentParam[val]
                    currentParam[name] = priorInfo['dist'](**priorInfo['params']).rvs()

        return currentParam

    def drawParameter(self):
        self._called += 1
        """Draw a value from the prior samples"""
        for name, samples in self._priorSamples.items():
            self._priorSet[name] = np.random.choice(samples)
        return self._priorSet

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
