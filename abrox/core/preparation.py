import pandas as pd
from model import UserDefinedModel


class Prepare:

    def __init__(self, config):
        self.config = config
        self.models = None

    def getObservedData(self, model):
        """
        Read in observed data or generate pseudo-observed data.
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
        Read in an external dataset, as specified by the user.
        :return: the data set as a numpy array.
        """
        try:
            return pd.read_csv(self.config['data']['datafile'],
                               delimiter=self.config['data']['delimiter']).as_matrix()

        except ImportError('Data file could not be imported'):
            return None

    def buildModels(self):
        """
        Generate list of models.
        :return: models
        """
        self.models = []
        for i, modelDict in enumerate(self.config['models']):
            self.models.append(UserDefinedModel(**modelDict))

        return self.models

    def getSummaryFunc(self):
        """ Return instance of summary class. """
        return self.config['summary']

    def getMetaInfo(self):
        """
        Get information needed for the algorithms to work.
        :return: a tuple of the five pieces of information
        """

        simulations = self.config['settings']['simulations']
        keep = self.config['settings']['keep']
        objective = self.config['settings']['objective']
        nModels = len(self.config['models'])
        parameterNames = [list(d.keys())[0] for d in self.config['models'][0]['prior']]

        return simulations, keep, objective, nModels, parameterNames
