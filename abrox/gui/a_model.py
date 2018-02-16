from PyQt5.QtWidgets import QMessageBox
import copy
import re
import os
from collections import OrderedDict
from datetime import datetime


class AInternalModel:
    """This class represents the internal model for an approximate bayesian estimation."""

    def __init__(self):

        # Initialize defaults
        self._methodDefaults = AInternalModel._initMethodDefault()

        # Create an analysis skeleton as a dict
        self._project = OrderedDict([
            ('Analysis',
                OrderedDict([
                    ('data', {'datafile': None,
                              'delimiter': None}),
                    ('models', [
                        AModel('Model1'),
                    ]),
                    ('summary', ""),
                    ('distance', ""),
                    ('settings', {
                        'outputdir': "",
                        'distance_metric': "default",
                        'objective': 'comparison',
                        'method': copy.deepcopy(self._methodDefaults['rejection']),
                        'test': {'model': None, 'fixed': OrderedDict()},
                        'reftable': {
                            'simulations': 10000,
                            'extref': None
                        },
                    })
                    ]
                )
             )
            ]
        )

    @staticmethod
    def _initMethodDefault():
        """Returns a dictionary with the method default settings."""

        return {
            'mcmc': {'algorithm': 'specs',
                     'specs': OrderedDict([
                         ('keep', 100),
                         ('threshold', None),
                         ('chl', 10000),
                         ('burn', 0),
                         ('thin', 1),
                         ('proposal', None),
                         ('start', None)])
                     },
            'rejection': {'algorithm': 'rejection',
                       'specs': OrderedDict([
                           ('keep', 100),
                           ('threshold', None),
                           ('cv', None)])
                       },
            'randomforest': {'algorithm': 'randomforest',
                       'specs': OrderedDict([
                           ('n_estimators', 200),
                           ('max_depth', None),
                           ('min_samples_split', 2),
                           ('min_samples_leaf', 1),
                           ('criterion', 'gini')])
                       }
        }

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

    def addObjective(self, objective):
        self._project['Analysis']['settings']['objective'] = objective

    def addRefTable(self, refDict):
        self._project['Analysis']['settings']['reftable'] = refDict

    def addMethod(self, methodDict):
        self._project['Analysis']['settings']['method'] = methodDict

    def addMethodSpecs(self, specsDict):
        self._project['Analysis']['settings']['method']['specs'] = specsDict

    def addDataFileAndDelimiter(self, datafile, delim):

        self._project['Analysis']['data']['datafile'] = datafile
        self._project['Analysis']['data']['delimiter'] = delim

    def addOutputDir(self, dirPath):
        self._project['Analysis']['settings']['outputdir'] = dirPath

    def addModelIndexForTest(self, idx):
        self._project['Analysis']['settings']['test']['model'] = idx

    def addFixedParameters(self, listOfTuples):

        self._project['Analysis']['settings']['test']['fixed'] = OrderedDict(listOfTuples)

    def selectedModelForTest(self):

        # Make sure a model is selected
        if self._project['Analysis']['settings']['test']['model'] is None or \
                                                              not self.selectedModelIndexValid():
            raise IndexError('No valid model selected for test!')
        idx = self._project['Analysis']['settings']['test']['model']
        return self._project['Analysis']['models'][idx]

    def selectedModelIndexValid(self):
        return False if self._project['Analysis']['settings']['test']['model'] < 0 else True

    def dataFile(self):
        return self._project['Analysis']['data']['datafile']

    def dataFileAndDelimiter(self):

        return self._project['Analysis']['data']['datafile'], \
               self._project['Analysis']['data']['delimiter']

    def modelTest(self):

        return self._project['Analysis']['settings']['test']['model']

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

    def objective(self):
        return self._project['Analysis']['settings']['objective']

    def outputDir(self):
        return self._project['Analysis']['settings']['outputdir']

    def externalReference(self):
        return self._project['Analysis']['settings']['reftable']['extref']

    def simulations(self):
        return self._project['Analysis']['settings']['reftable']['simulations']

    def models(self):
        """Returns the model list."""

        return self._project['Analysis']['models']

    def method(self):
        return self._project['Analysis']['settings']['method']

    def algorithm(self):
        return self._project['Analysis']['settings']['method']['algorithm']

    def algorithmSpecs(self):
        return self._project['Analysis']['settings']['method']['specs']

    def algorithmDefaultSpecs(self, method):

        return copy.deepcopy(self._methodDefaults[method]['specs'])

    def fixedParameters(self):
        return self._project['Analysis']['settings']['test']['fixed']

    def fileWithPathName(self):
        """
        Checks if directory exists, if exists, changes name so it matches.
        Assumes model has been checked for sanity!
        """

        if os.path.isdir(self._project['Analysis']['settings']['outputdir']):
            return self._project['Analysis']['settings']['outputdir'] + \
                   '/analysis_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.py'


    def deletePriorFromModel(self, idx, modelName):
        """Interface function to delete a prior fom a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                model.removePrior(idx)

    def clearData(self):
        self._project['Analysis']['data'] = {'datafile': None,
                                             'delimiter': None}

    def changeSetting(self, key, val):
        self._project['Analysis']['settings'][key] = val

    def setting(self, key):
        return self._project['Analysis']['settings'][key]

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

    def sanityCheckPassed(self, parent=None):
        """
        Checks whether model fields of current project are correct.
        Returns True if ok, False otherwise + displays a message explaining
        the problem.
        """

        # ===== Initialize message box ===== #
        msg = QMessageBox()
        errorTitle = 'Could not start an ABC process...'

        # ===== Check if any models specified ===== #
        if not self._project['Analysis']['models']:

            text = 'No models defined. Your project should contain at least one model.'
            msg.critical(parent, errorTitle, text)
            return False

        # ===== Check if data loaded when not doing a model test ===== #
        if self._project['Analysis']['settings']['test']['model'] is None and \
           not self._project['Analysis']['data']['datafile']:

            text = 'Since you are not performing a model test, ' \
                   'you a need to load a data file.'
            msg.critical(parent, errorTitle, text)
            return False

        # ===== Check if output dir specified ===== #
        if not self._project['Analysis']['settings']['outputdir']:
            text = 'No output dir in settings specified!'
            msg.critical(parent, errorTitle, text)
            return False

        # ===== Check if comparison AND models < 1 ===== #
        if self._project['Analysis']['settings']['objective'] == 'comparison' and \
            len(self._project['Analysis']['models']) < 2:

            text = 'You need at least two models for objective "comparison".'
            msg.critical(parent, errorTitle, text)
            return False

        # All checks passed, start process from caller
        return True

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
        """Returns an ordered dict representation of itself."""

        return OrderedDict([('name', self.name),
                            ('priors', self._priors),
                            ('simulate', self.simulate)])

    def __repr__(self):

        return 'AModel [Name: {}, Priors: {}'.format(self.name, self._priors)

    def __iter__(self):
        """Make iteration possible."""

        return iter(self._priors)


