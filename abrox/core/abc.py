from collections import OrderedDict
from scipy import stats
import numpy as np

from abrox.core.summary import Summary
from abrox.core.error_check import ErrorCheck
from abrox.core.preparation import Prepare
from abrox.core.rejection import Reject
from abrox.core.plot import Plotter
from abrox.core.preprocess import Preprocess
from abrox.core.report import Report
from abrox.core.wegmann import Wegmann
from abrox.core.mcmc import MCMC


class Abc:

    def __init__(self,config):
        self.config = config
        self.errorCheck()

    def errorCheck(self):
        check = ErrorCheck(self.config)
        check.run()

    def run(self):
        prepare = Prepare(self.config)
        modelList, modelNames = prepare.buildModel()
        simulations, keep, objective, nModels, paramNames = prepare.getMetaInfo()
        obsData = prepare.getObservedData(modelList)

        summaryClass = Summary(self.config['summary'])
        sumStatObsData = summaryClass.summarize(obsData)

        preprocess = Preprocess(modelList, summaryClass, sumStatObsData)

        preprocess.run(simulations, parallel=True, jobs=4)

        rejecter = Reject(preprocess.refTable.getRefTable(), paramNames, keep, objective)

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
