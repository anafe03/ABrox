from multiprocessing import Pool
from time import time
import numpy as np
import pandas as pd

# import classes from files
from .basemodel import Model
from .modelcollection import ModelCollection
from .paramEstimation import ParamEstimator
from .Logistic import Logistic
from .customException import SimulateFunctionError, MismatchError, ConfigurationError


# =======================================#
# Class with implementation of the
# ABC rejection algorithm
# =======================================#
class Abc:
    """The ABC algorithm."""

    def __init__(self, config):
        self.config = config
        self.observed_data = None
        self.jobs = 1
        self.checker()
        self.setModelList()
        self.setSettings()
        self.observedData()

    def checker(self):
        """ Checks the config for errors """

        # check if the main parts are set
        names = {'data', 'models', 'summary', 'distance', 'settings'}
        if names != set(self.config.keys()):
            raise ConfigurationError('The configuration file should contain the following keys: \n' +
                                     ','.join(names))

        # check if each model contains the necessary information
        for i, modelDict in enumerate(self.config['models']):
            if set(modelDict.keys()) != {'name', 'priors', 'simulate'}:
                raise ConfigurationError(
                    "A model needs to be provided with three keys: 'name', 'priors', and 'simulate'")

        # check if dataset is available, if not modeltest has to be True
        if not self.config['data'] and not self.config['settings']['modeltest']:
            raise ConfigurationError(
                'Either provide a dataset to be imported or run a model test by setting modeltest to True.')

    def setModelList(self):
        """ Store instances of basemodels in list for further processing """

        if not self.config['models']:
            raise ConfigurationError('No models defined.')

        self.models = []
        for i, modelDict in enumerate(self.config['models']):
            print(modelDict)
            self.models.append(Model(**modelDict))

        for model in self.models:
            model.summary = self.config['summary']
            if self.config['settings']['distance_metric'] == "custom":
                if not self.config['distance']:
                    raise ConfigurationError(
                        "If 'distance_metric' is set to 'custom', you have to provide your own distance function")
                else:
                    model.distance = self.config['distance']
            else:
                model.distance_metric = "euclidean"

    def setSettings(self):
        """ Store settings from config in members of class """

        self.nparticle = (self.config['settings']['particles'])

        # check if threshold should be computed
        if self.config['settings']['threshold'] == -1:
            self.threshold = []
        else:
            self.threshold = self.config['settings']['threshold']

        self.percentile = self.config['settings']['percentile']

        self.objective = self.config['settings']['objective']

        self.outdir = self.config['settings']['outputdir']

        if not self.outdir:
            raise ConfigurationError("Please provide a directory. Use '.' \
            if you want to use your current working directory")

        # check if a method for model comparison is set
        if self.objective == "comparison" and len(self.config['models']) < 2:
            raise ConfigurationError('Define at least two models for comparison.')

        if self.objective == "comparison" and not self.config['settings']['method']:
            raise ConfigurationError(
                "You need to provide a method for BF approximation. Either 'rejection' or 'logistic'")
        elif self.objective == "inference" and not self.config['settings']['method']:
            raise ConfigurationError('Do not specify a method when interested in inference')

        self.method = self.config['settings']['method']

    def observedData(self):
        """ Loads observed data or generates pseudo-observed data from model """

        if self.config['data']['datafile'] is not None and self.config['settings']['modeltest'] is False:
            # import observed data
            self.observed_data = self.loadData()
        else:
            flag = True
            for i, model in enumerate(self.models):
                if i == self.config['settings']['modeltest']:
                    params = self.config['settings']['fixedparameters']
                    self.observed_data = model.simulate(params)
                    flag = False
            if flag:
                raise ConfigurationError("Did you provide the correct model index?")

    def loadData(self):
        """Load/store the external dataset"""
        try:
            return pd.read_csv(self.config['data']['datafile'],
                               delimiter=self.config['data']['delimiter']).as_matrix()

        except ImportError('Imported data could not be stored'):
            return None

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
                arguments = [idx] * int(self.nparticle / len(self.models))
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

        return self.model_collection.saveResults(diff_time=diff_time,
                                                 threshold=self.model_collection.threshold,
                                                 method=self.method,
                                                 postMatrix=postMat,
                                                 outdir=self.outdir)
