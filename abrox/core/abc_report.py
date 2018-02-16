from collections import Counter, OrderedDict
from itertools import combinations
import pandas as pd
import numpy as np

from abrox.core.abc_utils import toArray


class ABCReporter:

    def __init__(self, table, modelNames, paramNames, objective, wd):
        self.table = table
        self.modelNames = modelNames
        self.paramNames = paramNames
        self.objective = objective
        self._wd = wd

    def initParamTable(self):
        """ Initialise the parameter table."""
        paramArray = toArray(self.table, 'param')
        return pd.DataFrame(paramArray, columns=self.paramNames)

    def bayesFactor(self):
        """
        Compute Bayes factor matrix.
        :return: Bayes factor matrix
        """

        nModels = len(self.modelNames)
        counterDict = {idx: 0 for idx in range(nModels)}

        counter = Counter(counterDict)

        counter.update(self.table['idx'])

        orderedCounter = OrderedDict(sorted(counter.items()))

        lowerPart = [b / a for a, b in list(combinations(orderedCounter.values(), 2))]
        upperPart = []
        for t in lowerPart:
            try:
                inverse = 1 / t
                upperPart.append(inverse)
            except ZeroDivisionError:
                upperPart.append(len(self.table))

        bfMatrix = np.ones((nModels, nModels))

        bfMatrix[np.tril_indices(nModels, -1)] = lowerPart
        bfMatrix[np.triu_indices(nModels, 1)] = upperPart

        df = pd.DataFrame(bfMatrix,columns=self.modelNames)
        df['Models'] = self.modelNames
        df.set_index('Models', inplace=True)
        return df

    def report(self):
        """
        Report final results depending on objective.
        :return: Either Bayes factor matrix (comparison) or parameter summaries.
        """
        if self.objective == "comparison":
            return self.bayesFactor()

        if self.objective == "inference":
            paramTable = self.initParamTable()
            paramTable.to_csv(self._wd + '/posteriorSamples_rej.csv')
            return paramTable.describe()

