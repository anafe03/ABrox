

from abrox.core.abc_summary import ABCSummary
from abrox.core.config_check import ConfigTester
from abrox.core.abc_initializer import ABCInitializer
from abrox.core.rejection import ABCRejection
from abrox.core.plot import Plotter
from abrox.core.abc_preprocess import ABCPreprocess
from abrox.core.report import Report
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

        obsData = prepare.getObservedData(modelList)

        simulations, keep, _, = prepare.getsimSettings()

        nModels = prepare.getModelNumber()

        paramNames = prepare.getParameterNames()

        objective = prepare.getObjective()

        algorithm, hyperParams = prepare.getAlgorithmInfo()

        summaryClass = ABCSummary(self.config['summary'])

        sumStatObsData = summaryClass.summarize(obsData)

        preprocess = ABCPreprocess(modelList, summaryClass, sumStatObsData)

        table = preprocess.preprocess(simulations, parallel=True, jobs=4)

        rejecter = ABCRejection(table, keep)

        subset, threshold = rejecter.reject() # CAUTION: This should not always run!

        if algorithm == "rejection":

            reporter = Report(subset, modelNames, paramNames, objective)
            return reporter.report()

        if algorithm == "mcmc":

            mcmc = MCMC(preprocess=preprocess,
                        paramNames=paramNames,
                        subset=subset,
                        threshold=threshold,
                        **hyperParams)

            samples, accepted = mcmc.run()

            plotter = Plotter(samples, paramNames)
            plotter.plot()

            return samples
