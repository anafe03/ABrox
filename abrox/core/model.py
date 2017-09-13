from functools import reduce
from operator import mul
import numpy as np
from collections import ChainMap
from distance import get_distance

# =========================================#
# Helper functions
# =========================================#


def saveSimulatedData(data, num):
    np.savetxt("/Users/ulf.mertens/Desktop/test/out{}.txt".format(num), data)


def product(factors):
    """Calculate the product of all given factors."""
    return reduce(mul, factors, 1.0)

# =========================================#
# Model class
# =========================================#


class Model:
    """Model implementation"""

    def __init__(self, model):
        self.model = model
        self.prior = model.prior
        self.distance_metric = model.distance_metric
        self.parameterList = []
        self.scaled_simsum = None
        self.distances = []
        self.scaled_obssum = None
        self.threshold = None
        self.accepted = None
        self.check_distance()

    @property
    def name(self):
        """Get the name of the model"""
        return self.model.name

    def __repr__(self):
        return 'Model(name = %r, prior = %r, metric = %r)'.format(
            self.model.name, self.prior, self.distance_metric)

    @property
    def size(self):
        """
        Get the number of accepted simulations which
        is the number of elements in the parameterList
        """
        return len(self.parameterList)

    def simulate(self, param, data=None):
        """Run simulation for this model, returning variables."""
        return self.model.simulate(param)

    def summary(self, data):
        """Calculate summary statistics from given variables."""
        return self.model.summary(data)

    def distance(self, simdata, obsdata):
        """Calculate the distance between given summary data."""
        return self.model.distance(simdata, obsdata)

    def sample_parameter(self):
        """
        Sample parameters from prior. If prior is not a distribution but
        a single value, store the single value instead of sampling (rvs).
        """
        priorDict = dict(ChainMap(*self.prior))
        if not priorDict:
            return priorDict
        samples = {}
        for key in priorDict.keys():
            samples[key] = priorDict[key].rvs()
        return samples

    @property
    def mean(self):
        """Get the mean of all parameters."""
        if self.parameterList:
            return np.vstack(self.parameterList).mean(axis=0)
        else:
            return None

    def check_distance(self):
        """
        Determine if a distance metric is chosen, otherwise use the
        user-defined one.
        """
        if self.distance_metric is not None:
            self.compute_distance = get_distance(self.distance_metric)
        else:
            self.compute_distance = self.distance

    def add_parameter(self, parameter):
        """Add parameter to the population."""
        self.parameterList.append(parameter)

    def add_simulated_summary(self, ss):
        """Add simulated summary to the list."""
        self.simulated_summaries.append(ss)
