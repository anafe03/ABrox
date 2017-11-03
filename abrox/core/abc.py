from collections import OrderedDict
from scipy import stats
import numpy as np

from abrox.core.summary import Summary
from abrox.core.config_check import ConfigTester
from abrox.core.preparation import ABCInitializer
from abrox.core.rejection import ABCRejection
from abrox.core.plot import Plotter
from abrox.core.preprocess import ABCPreprocess
from abrox.core.report import Report
from abrox.core.wegmann import Wegmann
from abrox.core.mcmc import MCMC


class Abc:
    """
    This is the class that organizes all steps required for
    a complete ABC analysis. The constructor calls the helper 
    class ConfigurationTester, which performs a sanity check on
    the config dictionary supplied by the user.
    """
    def __init__(self, config):
        self.config = config
        self._checkConfigSanity()

    def _checkConfigSanity(self):
        """Creates and runs an instance of the config sanity tester."""

        tester = ConfigTester(self.config)
        tester.checkForErrors()

    def run(self):
        """
        The only interface method of the class, responsible for handling
        all pre-processing and computation steps.
        """

        prepare = ABCInitializer(self.config)
        modelList, modelNames = prepare.buildModels()
        simulations, keep, objective, nModels, paramNames = prepare.getMetaInfo()
        obsData = prepare.getObservedData(modelList)

        summaryClass = Summary(self.config['summary'])
        sumStatObsData = summaryClass.summarize(obsData)

        preprocess = ABCPreprocess(modelList, summaryClass, sumStatObsData)

        table = preprocess.preprocess(simulations, parallel=True, jobs=4)

        rejecter = ABCRejection(table, paramNames, keep, objective)

        if self.config['settings']['method'] == "rejection":

            subset, _ = rejecter.reject()

            reporter = Report(subset, modelNames, paramNames, objective)
            return reporter.report()

        if self.config['settings']['method'] == "mcmc":

            if self.config['settings']['type'] == "wegmann":
                subset, threshold = rejecter.reject()

                wegmann = Wegmann(subset, paramNames, threshold)
                threshold = wegmann.threshold
                proposal = wegmann.getProposal()
                startingValues = wegmann.getStartingValues()

            chainLength = 10000
            burn = 100
            # proposalDist = OrderedDict([("d", stats.uniform(-0.05, 0.1))])
            mcmc = MCMC( preprocess = preprocess,
                         paramNames = paramNames,
                         chainLength = chainLength,
                         proposal = proposal,
                         threshold = threshold,
                         burn = burn)

            samples, accepted = mcmc.run(startingValues)

            plotter = Plotter(samples, paramNames)
            plotter.plot()

            return samples
