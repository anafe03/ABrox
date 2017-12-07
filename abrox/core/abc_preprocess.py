from multiprocessing import Pool
import numpy as np
import itertools


from abrox.core.abc_utils import euclideanDistance
from abrox.core.abc_reference_table import RefTable
from abrox.core.abc_scale import ABCScaler


class ABCPreProcessor:

    def __init__(self, model, summarizer, sumStatObsData):

        # Private attributes
        self._models = model
        self._refTableWrapper = RefTable()

        # Public attributes
        self.summarizer = summarizer
        self.scaler = ABCScaler()
        self.sumStatObsData = sumStatObsData
        self.scaledSumStatObsData = None

    def _generateSample(self, _, modelindex):
        """
        Run one simulation.
        1. Draw parameter from model
        2. Simulate data
        3. Compute summary statistics
        4. Add row to reference Table
        """
        param = self._models[modelindex].drawParameter()
        simdata = self._models[modelindex].simulate(param)
        sumstat = self.summarizer.summary(simdata)
        return modelindex, list(param.values()), sumstat, -1

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

        return self._models[0]

    def fillTable(self, simulations, parallel, jobs):
        """
        Run (summarize(simulate()) #simulation
        and store results in ABC table. Return summary statistics
        for scaling as numpy array.
        """

        args = self._generateArgs(simulations, len(self._models))
        with Pool(jobs) as pool:

            Starmap = pool.starmap if parallel else itertools.starmap
            out = Starmap(self._generateSample, args) if parallel else list(Starmap(self._generateSample, args))

        self._refTableWrapper.initialize(out)

        return self._refTableWrapper.getColumn('sumstat')

    def preprocess(self, simulations, parallel=True, jobs=2):
        """
        Generate the complete ABC reference table.
        :param sumStatObsData: summary statistics of observed data
        :param simulations: number of rows in the table
        :param parallel: boolean flag
        :param jobs: number of jobs if parallel
        :return: None
        """

        # Pre-fill table and return unscaled summary statistics
        sumStatTable = self.fillTable(simulations, parallel, jobs)

        # Scale summary statistics and store MAD
        scaledSumStatTable = self.scaler.fit_transform(sumStatTable)

        # Override unscaled with scaled summary statistics
        self._refTableWrapper.fillColumn(scaledSumStatTable, 'sumstat')

        # Scale observed summary statistics with MAD calculated above
        self.scaledSumStatObsData = self.scaler.transform(self.sumStatObsData)

        # Compute distance
        distance = euclideanDistance(scaledSumStatTable, self.scaledSumStatObsData)

        # Store distance in table
        self._refTableWrapper.fillColumn(distance, 'distance')

        return self._refTableWrapper.getRefTable()





