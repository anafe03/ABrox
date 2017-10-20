from collections import OrderedDict


class Model:
    """Model implementation"""

    def __init__(self, name, prior, simulate):
        self.name = name
        self.prior = prior
        self.currentParam = OrderedDict()
        self.simulate = simulate

    def name(self):
        """Get the name of the model"""
        return self.name

    def __repr__(self):
        return 'Model(name = {}, parameters = {})'.format(
            self.name, len(self.prior))

    def drawParameter(self):
        """ Draw a value from each prior distribution"""
        for priorDict in self.prior:
            for name, dist in priorDict.items():
                self.currentParam[name] = dist.rvs()
        return self.currentParam

    def simulate(self, param):
        """Simulate data"""
        return self.simulate(param)

