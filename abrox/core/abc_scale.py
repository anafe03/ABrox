import numpy as np


class ABCScaler:

    def __init__(self):
        self.summaryStats = None
        self.mad = None

    def _mad(self, x):
        """Median absolute deviation."""
        return np.median(np.abs(x - np.median(x)))

    def scale(self, summaryStats):
        """Compute MAD for each column."""
        self.mad = np.apply_along_axis(self._mad, 0, summaryStats)

    def fit_transform(self, summaryStats):
        """ Store MAD and return scaled summary statistics."""

        self.scale(summaryStats)
        return summaryStats / self.mad

    def transform(self, data):
        """Scale data using MAD computed from fit_transform."""

        data /= self.mad
        return data

