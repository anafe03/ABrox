import pandas as pd
from itertools import chain

from abrox.core.abcmodel import ABCModel


class ABCInitializer:

    def __init__(self, config):
        self.config = config
        self.model = None

    def getObservedData(self, model):
        """
        Import observed data or generate pseudo-observed data.
        :return: The (pseudo) observed data
        """

        if self.config['data']['datafile'] is not None:
            return self.loadExternalData()
        else:
            for i, model in enumerate(model):
                if i == self.config['settings']['modeltest']:
                    params = self.config['settings']['fixedparameters']
                    return model.simulate(params)

    def loadExternalData(self):
        """
        Import external dataset.
        :return: the dataset
        """
        try:
            return pd.read_csv(self.config['data']['datafile'],
                               delimiter=self.config['data']['delimiter']).as_matrix()

        except ImportError('Imported data could not be imported'):
            return None

    def buildModels(self):
        """
        Generate a list of models.
        :return: the list of models, and the model names
        """
        self.model = []
        for i, modelDict in enumerate(self.config['models']):
            self.model.append(ABCModel(**modelDict))
        modelNames = [model['name'] for model in self.config['models']]

        return self.model, modelNames

    def getSummaryFunc(self):
        """Returns an instance of summary class."""
        return self.config['summary']

    def flattenList(self, alist):
        return list(chain.from_iterable(alist))

    def getMetaInfo(self):
        """ Get number of simulations and how many should be accepted. """
        simulations = self.config['settings']['simulations']
        keep = self.config['settings']['keep']
        objective = self.config['settings']['objective']
        nModels = len(self.config['models'])
        parameterNames = self.flattenList([list(d.keys()) for d in self.config['models'][0]['prior']])

        return simulations, keep, objective, nModels, parameterNames
