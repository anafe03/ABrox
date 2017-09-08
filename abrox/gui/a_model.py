import copy
import re
import pprint


class AInternalModel:
    """This class represents the internal model for an approximate bayesian estimation."""
    def __init__(self):

        # Create an analysis skeleton as a dict
        self._project = {'Analysis': {
                            'data': {
                                'datafile': None
                            },
                            'models': [
                                AModel('Model1')
                            ],
                            'summary': "",
                            'distance': "",
                            'settings': {
                                'outputdir': "",
                                'distance_metric': "default",
                                'particles': 1000,
                                'threshold': -1,
                                'percentile': 0.05,
                                'objective': 'comparison',
                                'method': 'logistic',
                                'modeltest': False,
                                'fixedparameters': [

                                ]
                            }
                        }}

    def deleteModel(self, nameToRemove):
        """Interface function to remove a model."""

        for idx, model in enumerate(self._project['Analysis']['models']):
            if model.name == nameToRemove:
                self._project['Analysis']['models'].pop(idx)

    def renameModel(self, oldName, newName):
        """Interface function to rename a model."""

        for model in self._project['Analysis']['models']:
            if model.name == oldName:
                model.name = newName

    def addModel(self, name, simulate=None):
        """Interface function to add a new model."""

        model = AModel(name, simulate)
        self._project['Analysis']['models'].append(model)
        return model

    def addPriorToModel(self, paramName, sciPyCode, modelName):
        """Interface function to add a prior name:func to a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                # add priors returns T or F according to whether added ot not
                return model.addPrior(paramName, sciPyCode)

    def addSimulateToModel(self, simulateCode, modelName):
        """Interface function to add a prior name:func to a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                model.simulate = simulateCode

    def addSummary(self, summaryCode):
        self._project['Analysis']['summary'] = summaryCode

    def addDistance(self, distanceCode):
        self._project['Analysis']['distance'] = distanceCode

    def summary(self):
        """Returns the summary function code as a string."""

        return self._project['Analysis']['summary']

    def distance(self):
        """Returns the summary function code as a string."""

        if self._project['Analysis']['settings']['distance_metric'] == "default":
            return None
        else:
            return self._project['Analysis']['distance']

    def simulate(self):
        """Returns a dict with key-model name functions."""

        # Use this pattern to extract a function name
        pattern = r'(?<=def)(.*)(?=\()'

        simulateCodes = dict()
        for model in self._project['Analysis']['models']:
            # Get function name
            funcName = re.search(pattern, "def simulate():")
            funcName = funcName.group(1).strip()
            # Replace function name
            simulateCode = model.simulate.replace(funcName, funcName + '_' + model.name)
            simulateCodes[model.name] = (simulateCode, funcName + '_' + model.name)
        return simulateCodes

    def deletePriorFromModel(self, idx, modelName):
        """Interface function to delete a prior fom a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                model.removePrior(idx)

    def addDataFile(self, datafile):

        self._project['Analysis']['data']['datafile'] = datafile

    def dataFile(self):

        return self._project['Analysis']['data']['datafile']

    def changeSetting(self, key, val):
        self._project['Analysis']['settings'][key] = val

    def toDict(self):
        """Returns a dict representation of the entire session."""

        # Make a deep copy fo the project
        projectCopy = copy.deepcopy(self._project)

        # Turn model objects into dicts
        projectCopy['Analysis']['models'] = []
        for model in self._project['Analysis']['models']:
            projectCopy['Analysis']['models'].append(model.toDict())
        return projectCopy

    def overwrite(self, newProject):
        """Overwrites project data member with new project, also creates models."""

        # Create a copy of the project
        self._project = copy.deepcopy(newProject)

        # Create models from the model dicts and add them to the list of models
        newModels = [AModel.fromDict(model) for model in self._project['Analysis']['models']]
        self._project['Analysis']['models'] = newModels

    def models(self):
        """Returns the model list."""

        return self._project['Analysis']['models']

    def __iter__(self):
        """Make iteration possible."""

        return iter(self._project['Analysis'])

    def __getitem__(self, key):
        return self._project['Analysis'][key]


class AModel:
    """
    This class represents an individual 
    statistical model amenable to ABrox analysis.
    """

    @classmethod
    def fromDict(cls, modelDict):

        model = cls(modelDict['name'], modelDict['simulate'])
        model._priors = modelDict['priors']
        return model

    def __init__(self, name, simulate=None):

        self.name = name
        self.simulate = simulate
        self._priors = []

    def removePrior(self, idx):
        """Interface to remove a prior."""

        self._priors.pop(idx)

    def addPrior(self, priorName, sciPyCode):
        """Insert a prior (dict with name and function code."""

        # Check if name taken
        for prior in self._priors:
            if list(prior.keys())[0] == priorName:
                return False
        # Name not taken, append
        self._priors.append({priorName: sciPyCode})
        return True

    def hasPriors(self):
        return any(self._priors)

    def toDict(self):
        """Returns a dict representation of itself."""

        return {'name': self.name,
                'priors': self._priors,
                'simulate': self.simulate}

    def __repr__(self):

        return 'AModel [Name: {}, Priors: {}'.format(self.name, self._priors)

    def __iter__(self):
        """Make iteration possible."""

        return iter(self._priors)


