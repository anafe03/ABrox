import numpy as np
from abrox.core.abc_utils import toArray, euclideanDistance


class ABCCv:

    def __init__(self, refTable, keep):
        self.refTable = refTable
        self.sumStatArray = toArray(self.refTable,'sumstat')
        self.paramArray = toArray(self.refTable,'param')
        self.indexList = np.arange(len(self.refTable.index))
        self.picks = []
        self.keep = keep

    def _getRandomIndices(self):
        """
        Pick a random row index from the reference table and the remaining indices.
        :return: both the picked index and the remaining indices.
        """
        picked = np.random.choice(self.indexList)


        self.picks.append(picked)

        notPicked = self.indexList[self.indexList != picked]
        return picked, notPicked

    def calculateDistance(self, picked, notPicked):
        """
        Compute distances between all simulated summary statistics and
        the pseudo-observed summary statistic
        :return: distances (one less then the number of rows of refTable)
        """
        distances = euclideanDistance(self.sumStatArray[notPicked], self.sumStatArray[picked])
        return distances

    def deletePickedRow(self,picked):
        """
        Drop the picked row from the reference table.
        :param picked: integer representing the row-index.
        :return: None
        """
        subTable = self.refTable.drop(self.refTable.index[[picked]], inplace=False)
        return subTable

    def subset(self, subTable):
        """
        Return tuple with filtered Reference Table only containing
        rows for which the distance is < threshold and threshold itself.
        :return: the tuple
        """
        q = self.keep / len(subTable.index) * 100
        threshold = np.percentile(subTable['distance'],q=q)
        subset = subTable[subTable['distance'] < threshold]
        return subset

    def getEstimates(self,subset):
        """
        Compute mean for each parameter in subset.
        :param subset: the subset table.
        :return: the means (estimates)
        """
        paramArray = toArray(subset,'param')
        return np.mean(paramArray, axis=0)

    def cv(self,times=100):
        """
        Run cross validation scheme:
            - pick a simulated summary statistic from the ref table.
            - treat it as pseudo-observed
            - compute the distances between all other and the pseudo-observed one.
            - run rejection algorithm as usual.
        :param times: accuracy of cv.
        :return: the array of estimated parameters.
        """
        cols = len(self.refTable.at[0,'param'])
        estimatedParams = np.empty(shape=(times,cols))

        for i in range(times):
            picked, notPicked = self._getRandomIndices()
            distances = self.calculateDistance(picked, notPicked)
            subTable = self.deletePickedRow(picked)
            subTable['distance'] = distances
            subset = self.subset(subTable)
            estimatedParams[i,:] = self.getEstimates(subset)

        return estimatedParams

    def report(self):
        """
        Compute the prediction error.
        :return: the error.
        """
        estimatedParams = self.cv()
        trueParams = self.paramArray[self.picks,:]

        SumSqDiff = np.sum((estimatedParams - trueParams)**2,axis=0)
        Variance = np.var(trueParams,axis=0)

        return np.float(SumSqDiff / Variance)


