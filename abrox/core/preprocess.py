from multiprocessing import Pool
import numpy as np
import itertools
from abc_utils import euclideanDistance


class AbcPreprocesser:

    def __init__(self, model, summarizer, reftable, scaler):
        self.model = model
        self.summarizer = summarizer
        self.refTable = reftable
        self.scaler = scaler
        self.scaledSumStatObsData = None

    def _generateSample(self, simN, modelIndex):
        """
        Compute one simulation.
        1. Draw parameter from model modelIndex
        2. Simulate data
        3. Compute summary statistics
        4. Add row to ABC Table
        """
        param = self.model[modelIndex].drawParameter()
        simdata = self.model[modelIndex].simulate(param)
        sumstat = self.summarizer.summary(simdata)
        return modelIndex, list(param.values()), sumstat, -1

    def _generateArgs(self, simulations, nModels):
        """
        Generate argument list.
        :param simulations:
        :param nModels:
        :return:
        """
        iterations = np.tile(np.arange(simulations), nModels)
        modelindices = np.repeat(np.arange(nModels), simulations)
        return list(zip(iterations, modelindices))

    def getFirstModel(self):
        """
        Get first model from list of models. This is
        necessary for parameter inference via MCMC.
        """
        return self.model[0]

    def fillTable(self, simulations, parallel, jobs):
        """
        Run (summarize(simulate()) #simulation
        and store results in ABC table. Return summary statistics
        for scaling as numpy array.
        """

        args = self._generateArgs(simulations, len(self.model))
        with Pool(jobs) as pool:
            Starmap = pool.starmap if parallel else itertools.starmap
            out = Starmap(self._generateSample, args) if parallel else list(Starmap(self._generateSample, args))

        self.refTable.initialize(out)

        return self.refTable.getColumn('sumstat')

    def preprocess(self, sumStatObsData, simulations, parallel=True, jobs=4):
        """
        Generate Reference Table.
        :param sumStatObsData: summary statistics of observed data
        :param simulations: number of rows in the table
        :param parallel: boolean flag
        :param jobs: number of jobs if parallel
        :return: None
        """

        # prefill table and return unscaled summary statistics
        sumStatTable = self.fillTable(simulations, parallel, jobs)
        # scale summary statistics and store MAD
        scaledSumStatTable = self.scaler.fit_transform(sumStatTable)
        # override unscaled with scaled summary statistics
        self.refTable.fillColumn(scaledSumStatTable, 'sumstat')
        # scale observed summary statistics with MAD calculated above
        self.scaledSumStatObsData = self.scaler.transform(sumStatObsData)
        # compute distance
        distance = euclideanDistance(scaledSumStatTable, self.scaledSumStatObsData)
        # store distance in table
        self.refTable.fillColumn(distance, 'distance')
        # return reference table
        return self.refTable.getTable()


if __name__ == "__main__":
    pass






