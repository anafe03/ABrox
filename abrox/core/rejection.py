import numpy as np
from scipy import stats

from abrox.core.reference_table import RefTable
from abrox.core.summary import Summary
from abrox.core.error_check import ErrorCheck
from abrox.core.preparation import Prepare
from abrox.core.scale import Scaler
from abrox.core.preprocess import Preprocess
from abrox.core.report import Report


class Reject:

    def __init__(self, refTable, paramNames, keep, objective):
        self.refTable = refTable
        self.paramNames = paramNames
        self.keep = keep
        self.obj = objective
        self.paramTable = None

    def reject(self):
        """
        Return filtered Reference Table only containing
        rows for which the distance is < threshold.
        """
        q = self.keep / len(self.refTable.index) * 100
        threshold = np.percentile(self.refTable['distance'],q=q)
        return self.refTable[self.refTable['distance'] < threshold]


def summary(data):
    data_mean = np.mean(data, axis=0)
    diff_mean = data_mean[0] - data_mean[1]
    mean_std = np.mean(np.std(data, axis=0))
    return diff_mean / mean_std

def simulate_Model1(params):
    n = 100
    first_sample = np.random.normal(0, 1, n)
    sec_sample = np.random.normal(params['d'], 1, n)
    return np.column_stack((first_sample, sec_sample))

def simulate_Model2(params):
    n = 100
    first_sample = np.random.normal(0, 1, n)
    sec_sample = np.random.normal(0, 1, n)
    return np.column_stack((first_sample, sec_sample))


CONFIG = {
    "data": {
        "datafile": None,
        "delimiter": None
    },
    "models": [
        {
        "name": "Model1",
        "prior": [
            {"d": stats.cauchy(loc=0.0, scale=0.7)},
        ],
        "simulate": simulate_Model1
        },
        {
        "name": "Model2",
        "prior": [
        ],
        "simulate": simulate_Model2
        },
    ],
    "summary": summary,
    "distance": None,
    "settings": {
        'distance_metric': 'default',
         'fixedparameters': {'d': 0.3},
         'method': 'rejection',
         'modeltest': 0,
         'objective': 'comparison',
         'outputdir': '/Users/ulf.mertens/Desktop/abrox_demo/t_test',
         'simulations': 10000,
         'keep': 100,
         'threshold': -1
    }
}


if __name__ == "__main__":

    errorCheck = ErrorCheck(CONFIG)
    errorCheck.run()

    prepare = Prepare(CONFIG)

    modelList, modelNames = prepare.buildModel()

    simulations, keep, objective, nModels, paramNames = prepare.getMetaInfo()

    obsData = prepare.getObservedData(modelList)

    # IMPORTANT: multiprocessing seems to only work if summary is passed directly.
    # Building an instance of the summary class from within a method doesn't work.
    summaryClass = Summary(summary)
    sumStatObsData = summaryClass.summarize(obsData)

    abcTable = RefTable()
    scaler = Scaler()

    preprocess = Preprocess(modelList, summaryClass, abcTable, scaler)

    preprocess.run(sumStatObsData,simulations, parallel=True, jobs=4)

    # ABC rejection
    rejecter = Reject(preprocess.refTable.getRefTable(), paramNames, keep, objective)

    subset = rejecter.reject()

    reporter = Report(subset, modelNames, paramNames, objective)
    print(reporter.report())

    # TODO:
    # Sampling parameters is currently not really fast since the prior
    # distributions are the values from dicts in lists.
    # The draw_Parameter method in Model class needs to access these
    # values every time. I am not sure how this slows down the whole process.
