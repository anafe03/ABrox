from collections import OrderedDict
from scipy import stats
import numpy as np

from abrox.core.summary import Summary
from abrox.core.error_check import ErrorCheck
from abrox.core.preparation import Prepare
from abrox.core.rejection import Reject
from abrox.core.preprocess import Preprocess
from abrox.core.report import Report
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

        if self.config['settings']['method'] == "rejection":
            rejecter = Reject(preprocess.refTable.getRefTable(), paramNames, keep, objective)

            subset = rejecter.reject()

            reporter = Report(subset, modelNames, paramNames, objective)
            return reporter.report()

        if self.config['settings']['method'] == "mcmc":
            threshold = 0.05
            chainLength = 10000
            proposalDist = OrderedDict([("d", stats.uniform(-0.05, 0.1))])
            mcmc = MCMC(preprocess, proposalDist, paramNames, threshold, chainLength)
            start = np.array([0.6])
            samples, accepted = mcmc.run(start)

            # plotter = plotPosterior(samples, paramNames)
            # plotter.plot()

            return samples
