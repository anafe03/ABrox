"""Perturbation Kernels to be used with the ABC SMC algorithm."""

from math import exp, pi, sqrt
import numpy as np


INV_SQRT_2PI = 1 / sqrt(2 * pi)


def get_kernel(prior):
    """Get a perturbation kernel for the given prior distribution."""
    if isinstance(prior, (int, float)):
        name = "point-null"
        return None
    else:
        name = prior.dist.name
        args = prior.args
        if name == 'norm' or name == 'cauchy' or name == 'gamma':
            kernel = NormalKernel
        elif name == 'uniform':
            args = (0.5 * (args[0] + (args[0] + args[1])), 0.5 * args[1])
            kernel = UniformKernel
        else:
            raise ValueError('Cannot get a suitable kernel.')
        return kernel(*args)


class Kernel:
    """Base class for fast perturbation kernels."""

    def __init__(self, mode=0, scale=1):
        self.mode, self.scale = float(mode), float(scale)

    def pdf(self, x):
        raise NotImplementedError

    def rvs(self):
        raise NotImplemented

    def update(self, previous_params):
        raise NotImplemented


class NormalKernel(Kernel):
    """Kernel for normal distribution."""

    def pdf(self, x):
        a = (x - self.mode) / self.scale
        return INV_SQRT_2PI / self.scale * exp(-0.5 * a * a)

    def rvs(self):
        return np.random.normal(loc=self.mode, scale=self.scale)

    def update(self, params):
        self.scale = 2 * np.var(params)


class UniformKernel(Kernel):
    """Kernel for uniform distribution."""

    def pdf(self, x):
        if self.mode - self.scale <= x <= self.mode + self.scale:
            return 1.0 / (self.scale * 2)
        else:
            return 0.0

    def rvs(self):
        return np.random.uniform(
            low=self.mode - self.scale, high=self.mode + self.scale)

    def update(self, params):
        self.scale = 0.5 * (np.max(params) - np.min(params))
