
class ConfigurationError(Exception):
    pass


class ConfigTester:

    def __init__(self, config):
        self.config = config

    def _checkMetaStructure(self):
        """
        Checks if the necessary keys of the config dictionary are used.
        :return: None
        """
        names = {'data', 'models', 'summary', 'distance', 'settings'}
        if names != set(self.config.keys()):
            raise ConfigurationError('The configuration file should contain the following keys: \n' +
                                     ','.join(names))

    def _checkModelStructure(self):
        """
        Checks if the model key contains the necessary information.
        :return: None
        """
        for i, modelDict in enumerate(self.config['models']):
            if set(modelDict.keys()) != {'name', 'priors', 'simulate'}:
                raise ConfigurationError(
                    "A model needs to be provided with three keys: 'name', 'priors', and 'simulate'")

    def _checkDataSetting(self):
        """
        Checks if a dataset is imported, if not then the option for model testing has to be set.
        :return: None
        """
        if not self.config['data'] and not self.config['settings']['modeltest']:
            raise ConfigurationError(
                'Either provide a dataset to be imported or run a model test by setting modeltest to True.')

    def _checkModelContent(self):
        """
        Check if model information is provided.
        :return: None
        """
        if not self.config['models']:
            raise ConfigurationError('No models defined.')

    def _checkDistanceSettings(self):
        """
        Check if distance function is provided.
        :return: None
        """
        if self.config['settings']['distance_metric'] == "custom":
            if not self.config['distance']:
                raise ConfigurationError(
                    "If 'distance_metric' is set to 'custom', you have to provide your own distance function")

    def _checkDirectory(self):
        """
        Check if a directory is specified.
        :return: None
        """
        if not self.config['settings']['outputdir']:
            raise ConfigurationError("Please provide a directory. Use '.' \
            if you want to use your current working directory")

    def _checkObjective(self):
        """
        Check if objective setup is correct.
        :return: None
        """
        # check if a method for model comparison is set
        if self.config['settings']['objective'] == "comparison" and len(self.config['models']) < 2:
            raise ConfigurationError('Define at least two models for comparison.')

        if self.config['settings']['objective'] == "inference" and len(self.config['models']) > 1:
            raise ConfigurationError('Please define only one model for parameter inference.')

    def checkForErrors(self):
        """
        Run all sanity tests on the config file.
        :return: None
        """
        self._checkMetaStructure()
        self._checkModelStructure()
        self._checkDataSetting()
        self._checkModelContent()
        self._checkDistanceSettings()
        self._checkDirectory()
        self._checkObjective()
