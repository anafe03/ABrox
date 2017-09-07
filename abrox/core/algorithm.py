import itertools
from multiprocessing import Pool
from time import time
from tqdm import tqdm
import numpy as np

# import classes from files
from basemodel import Model
from modelcollection import ModelCollection
from paramEstimation import ParamEstimator
from Logistic import Logistic
from customException import SimulateFunctionError, MismatchError, ConfigurationError


# =======================================#
# Class with implementation of the
# ABC rejection algorithm
# =======================================#

class Abc:
    """The ABC algorithm."""

    def __init__(self, configFile):
        self.configFile = configFile
        self.jobs = 1
        self.checker()
        self.setModelList()
        self.setSettings()
        self.observedData()

    def checker(self):
        """ Checks the configFile for errors """

        # check if the main parts are set
        names = {'data', 'models', 'summary', 'distance', 'settings'}
        if names != set(self.configFile.keys()):
            raise ConfigurationError('The configuration file should contain the following keys: \n' +
                                     ','.join(names))

        # check if each model contains the necessary information
        for i, modelDict in enumerate(self.configFile['models']):
            if set(modelDict.keys()) != {'name', 'priors', 'simulate'}:
                raise ConfigurationError(
                    "A model needs to be provided with three keys: 'name', 'priors', and 'simulate'")

        # check if dataset is available, if not modeltest has to be True
        if not self.configFile['data'] and not self.configFile['settings']['modeltest']:
            raise ConfigurationError(
                'Either provide a dataset to be imported or run a model test by setting modeltest to True.')

    def setModelList(self):
        """ Store instances of basemodels in list for further processing """
        self.models = []
        for i, modelDict in enumerate(self.configFile['models']):
            print(modelDict)
            self.models.append(Model(**modelDict))

        for model in self.models:
            model.summary = self.configFile['summary']
            if self.configFile['settings']['distance_metric'] == "custom":
                if not self.configFile['distance']:
                    raise ConfigurationError(
                        "If 'distance_metric' is set to 'custom', you have to provide your own distance function")
                else:
                    model.distance = self.configFile['distance']
            else:
                model.distance_metric = "euclidean"

    def setSettings(self):
        """ Store settings from configFile in members of class """
        self.nparticle = self.configFile['settings']['particles']

        # check if threshold should be computed
        if self.configFile['settings']['threshold'] == -1:
            self.threshold = []
        else:
            self.threshold = self.configFile['settings']['threshold']

        self.percentile = self.configFile['settings']['percentile']

        self.objective = self.configFile['settings']['objective']

        # check if a method for model comparison is set
        if self.objective == "comparison" and not self.configFile['settings']['method']:
            raise ConfigurationError(
                "You need to provide a method for BF approximation. Either 'rejection' or 'logistic'")
        elif self.objective == "inference" and not self.configFile['settings']['method']:
            raise ConfigurationError('Do not specify a method when interested in inference')

        self.method = self.configFile['settings']['method']

    def observedData(self):
        """ Loads observed data or generates pseudo-observed data from model """
        if self.configFile['data'] and not self.configFile['settings']['modeltest']:
            # import observed data
            self.observed_data = self.loadData(self.configFile)
        else:
            flag = True
            for i, model in enumerate(self.models):
                if model.name == self.configFile['settings']['modeltest']:
                    params = self.configFile['settings']['fixedparameters']
                    self.observed_data = model.simulate(params)
                    flag = False
            if flag:
                raise ConfigurationError("Did you provide the correct model name in 'modeltest'?")

    def loadData(self):
        try:
            self.data = np.loadtxt(self.configFile['data'])  # pandas
        except:
            raise ImportError('The data file located at ' +
                              self.configFile[0] + ' could not be imported')

    def create_particle(self, model_index=None):
        """Generate particle"""
        return self.model_collection.create_particle(model_index)

    def transfer(self, result):
        """Add necessary infos"""

        model_index, param, simsum = result
        self.model_collection.transfer(
            model_index=model_index,
            param=param,
            simsum=simsum)

    def postprocess(self):
        """Post-processing work."""
        # Compute scaled simulated summary statistic
        sumstats = self.model_collection.scale()
        # compute distance based on scaled version
        self.model_collection.computeDistance(sumstats)
        # compute the threshold based on distances
        self.model_collection.computeThreshold()
        # pass scaled summary statistics to models
        self.model_collection.passToModel(sumstats)

        if self.method == "rejection":
            self.model_collection.computeAcceptance()

    def run(self):
        """Run the algorithm"""

        start_time = time()

        # construct ModelCollection instance from
        # list of models
        self.model_collection = ModelCollection(self.models)

        # check shape
        for model in self.model_collection:
            param = model.sample_parameter()
            if type(model.simulate(param)) is not np.ndarray:
                raise SimulateFunctionError(
                    'Simulate function must return array of type np.ndarray')
            if not model.simulate(param).shape == self.observed_data.shape:
                raise MismatchError('''Make sure that your observed dataset has
                                 the same shape as the simulated dataset''')

        # compute summary of observed data
        self.observed_summary = self.model_collection[0].summary(self.observed_data)

        # add observed summary statistic to model collection
        self.model_collection.obssum = self.observed_summary

        # add percentile to model Collection
        self.model_collection.percentile = self.percentile

        # =========================================== #
        # START THE ALGORITHM
        # =========================================== #

        with Pool(self.jobs) as pool:

            Map = map if self.jobs == 1 else pool.map

            # create particles in parallel

            for idx in range(len(self.models)):
                arguments = [idx] * (self.nparticle // len(self.models))
                results = Map(self.create_particle, arguments)
                # add each particle
                for result in results:
                    self.transfer(result)

        print("\n\nSimulation of {0} datasets finished\n".
              format(self.nparticle))

        self.postprocess()  # scale simulated summaries

        postMat = None

        if self.objective == "inference":

            Param_estimator = ParamEstimator(self.model_collection)
            postMat = Param_estimator.run()

        else:  # objective == comparison
            if self.method == "logistic":
                logisticHandler = Logistic(self.model_collection)
                logisticHandler.run()

        diff_time = time() - start_time
        return self.model_collection.report(diff_time=diff_time,
                                            threshold=self.model_collection.threshold,
                                            method=self.method,
                                            postMatrix=postMat)
