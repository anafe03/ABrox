import numpy as np


class ABCRejection:

    def __init__(self, refTable, keep):
        self.refTable = refTable
        self.keep = keep

    def reject(self):
        """
        Return tuple with filtered Reference Table only containing
        rows for which the distance is < threshold and threshold itself.
        :return: the tuple
        """
        q = self.keep / len(self.refTable.index) * 100
        threshold = np.percentile(self.refTable['distance'],q=q)
        subset = self.refTable[self.refTable['distance'] < threshold]
        return subset, threshold
