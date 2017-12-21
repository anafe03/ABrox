import pandas as pd
from itertools import chain

from abrox.core.abc_model import ABCModel


class ABCInitializer:

    def __init__(self, config):
        self.config = config
        self.model = None

    def getOrGenerateObsData(self, model):
        """
        Import observed data or generate pseudo-observed data.
        :return: The (pseudo) observed data as a numpy array.
        """

        if self.config['data']['datafile']:
            return self._loadExternalData()
        else:
            for i, model in enumerate(model):
                if i == self.config['settings']['test']['model']:
                    params = self.config['settings']['test']['fixed']
                    return model.simulate(params)

    def buildAndGetModels(self):
        """
        Generate a list of models.
        :return: the list of models, and the model names
        """
        self.model = []
        for i, modelDict in enumerate(self.config['models']):
            self.model.append(ABCModel(**modelDict))
        modelNames = [model['name'] for model in self.config['models']]

        return self.model, modelNames

    def extractAndGetSettings(self):
        """Extracts the relevant preporcessing and algorithm settings."""

        algo = self.config['settings']['method']['algorithm']
        specs = self.config['settings']['method']['specs']
        paramNames = self._getParameterNames()
        objective = self.config['settings']['objective']
        nModels = len(self.config['models'])
        reftable = self.config['settings']['reftable']
        outputdir = self.config['settings']['outputdir']

        settings = {'alg': algo,
                    'specs': specs,
                    'pnames': paramNames,
                    'obj': objective,
                    'nmodels': nModels,
                    'nsim': reftable['simulations'],
                    'extref': reftable['extref'],
                    'outputdir': outputdir
                    }

        return settings

    def getSummaryFunc(self):
        """Returns an instance of summary class."""
        return self.config['summary']

    def _flattenList(self, alist):
        return list(chain.from_iterable(alist))

    def _getParameterNames(self):
        """
        Returns parameter names of first model only!!
        """
        return self._flattenList([list(d.keys()) for d in self.config['models'][0]['priors']])

    def _loadExternalData(self):
        """
        Import external dataset.
        :return: the dataset
        """

        return pd.read_csv(self.config['data']['datafile'], engine='python',
                            delimiter=self.config['data']['delimiter']).as_matrix()








