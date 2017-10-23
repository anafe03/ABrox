from collections import OrderedDict


class UserDefinedModel:
    """Model implementation"""

    def __init__(self, name, prior, simulate):
        self.name = name
        self.prior = prior
        self.currentParam = OrderedDict()
        self.simulate = simulate

    def drawParameter(self):
        """
        Draw a value from each prior distribution and return it.
        :return: na ordered dict of parameters
        """
        for priorDict in self.prior:
            for name, dist in priorDict.items():
                self.currentParam[name] = dist.rvs()
        return self.currentParam

    def simulate(self, param):
        """
        Simulate data from user-defined simulate function.
        :param param: a dictionary with parameter-names : parameter-values
        :return: the output ot the simulate function
        """
        return self.simulate(param)

    def __repr__(self):
        """Provides a nice representation of the user defined model."""

        return 'Model:(name={}, params={})'.format(
            self.name, [list(prior.keys())[0] for prior in self.prior])


