import pprint
import datetime
from collections import OrderedDict


class AScriptCreator:
    """
    Handles the creation of a runnable python script. Accepts the gui model
    as first parameter and uses its interface to get the information needed.
    fileName is the name of the python file to-be-created.
    """

    def __init__(self, internalModel):

        self._internalModel = internalModel
        self.scriptName = None

    def createScript(self):
        """
        Creates an abs runnable script with the file name provided by model.
        Assumes that model sanity checks have been passed!
        """

        fileName = self._internalModel.fileWithPathName()

        # Get a dictionary of modelName: sim function code
        simulateDict = self._internalModel.simulate()

        # Get project dict and remove project name, since
        # config file does not need a project name
        projectDict = self._internalModel.toDict()
        projectDict = {k: v for value in projectDict.values()
                       for k, v in value.items()}

        # Open file and write components
        with open(fileName, 'w') as outfile:
            self._writeHeader(outfile)
            self._writeImports(outfile)
            self._writeSummaryAndDistFunc(outfile)
            self._writeSimulateFuncs(outfile, simulateDict)
            self._writeConfig(outfile, projectDict, simulateDict)
            self._writeAlgorithmCall(outfile)

        # Return filename for process manager
        return fileName

    def _writeHeader(self, outfile):
        """Write header with info and date."""

        header = '"""\n' \
                 'This is an automatically generated script by ABrox GUI.\n' \
                 'Created on {}.\n' \
                 '"""\n\n'.format(datetime.datetime.now())
        outfile.write(header)

    def _writeImports(self, outfile):
        """Write imports needed for abc."""

        imports = '# Required imports\n' \
                  'import numpy as np\n' \
                  'from scipy import stats\n' \
                  'from abrox.core.abc import Abc\n\n\n'

        outfile.write(imports)

    def _writeSummaryAndDistFunc(self, outfile):
        """Write summary and distance (if specified) code."""

        # Write summary
        outfile.write(self._internalModel.summary())
        outfile.write('\n\n\n')

        # Write distance
        if self._internalModel.distance() is not None:
            outfile.write(self._internalModel.distance())
            outfile.write('\n\n\n')

    def _writeSimulateFuncs(self, outfile, simulateDict):
        """Write simulate functions code."""

        for key in simulateDict:
            # The value of simulateDict is a 2-tuple (0 - code, 1 - name)
            outfile.write(simulateDict[key][0])
            outfile.write('\n\n\n')

    def _writeConfig(self, outfile, projectDict, simulateDict):
            """Creates the config file in a nice format. Pretty nasty."""


            # Write var name
            outfile.write('CONFIG = {\n')
            # Write data file and delimiter
            outfile.write('{}"data": {{\n'.format(self.tab()))
            if projectDict['data']['datafile']:
                outfile.write('{}"datafile": "{}",\n'.format(self.tab(2),
                                                        projectDict['data']['datafile']))
                outfile.write('{}"delimiter": "{}"\n'.format(self.tab(2),
                                                        projectDict['data']['delimiter']))
            else:
                outfile.write('{}"datafile": {},\n'.format(self.tab(2),
                                                             projectDict['data']['datafile']))
                outfile.write('{}"delimiter": {}\n'.format(self.tab(2),
                                                             projectDict['data']['delimiter']))
            outfile.write('{}}},\n'.format(self.tab()))

            # Write models
            outfile.write('{}"models": [\n'.format(self.tab()))
            for model in projectDict['models']:
                outfile.write('{}{{\n'.format(self.tab(2)))
                outfile.write('{}"name": "{}",\n'.format(self.tab(2),
                                                         model['name']))
                # Write priors
                outfile.write('{}"priors": [\n'.format(self.tab(2)))
                for prior in model['priors']:
                    outfile.write('{}{{"{}": {}}},\n'.format(self.tab(3),
                                                             list(prior.keys())[0],
                                                             list(prior.values())[0]))
                # Close priors list
                outfile.write('{}],\n'.format(self.tab(2)))

                # Write simulate
                outfile.write('{}"simulate": {}\n'.format(self.tab(2),
                                                          simulateDict[model['name']][1]))
                # Close this model dict
                outfile.write('{}}},\n'.format(self.tab(2)))
            # Close models list
            outfile.write('{}],\n'.format(self.tab()))

            # Write summary
            outfile.write('{}"summary": summary,\n'.format(self.tab()))

            # Write distance
            outfile.write('{}"distance": {},\n'.format(self.tab(),
                                                       'distance' if projectDict['settings']
                                                       ['distance_metric'] == 'custom' else None))

            # Write settings
            outfile.write('{}"settings": {{\n'.format(self.tab()))
            # Format settings dict using pprint
            self._orderedDictToDict(projectDict['settings'])

            settings = pprint.pformat(dict(projectDict['settings'])).replace('{', "", 1)
            settings = self._rreplace(settings, '}', '', count=1)

            # Indent output of pprint with 8 spaces
            settings = ''.join(['{}{}'.format(self.tab(2), l) for l in settings.splitlines(True)])
            outfile.write(settings)
            # Close settings dict
            outfile.write('\n{}}}\n'.format(self.tab()))
            # Close config dict
            outfile.write('}\n\n\n')

    def _writeAlgorithmCall(self, outfile):
        """Writes the algorithm call enclosed in an if __name__ == ..."""

        call = 'if __name__ == "__main__":\n' \
               '{}# Create and run an Abc instance\n' \
               '{}abc = Abc(config=CONFIG)\n' \
               '{}abc.run()\n'.format(self.tab(), self.tab(), self.tab())

        outfile.write(call)

    def _orderedDictToDict(self, d):
        """Converts all instances of OrderedDict to dict recursively."""

        for k, v in d.items():
            if isinstance(v, dict):
                if isinstance(v, OrderedDict):
                    d[k] = dict(v)
                self._orderedDictToDict(d[k])

    def _rreplace(self, s, old, new, count=1):
        """A helper function to replace strings backwards."""
        li = s.rsplit(old, count)
        return new.join(li)

    def tab(self, s=1):
        """Returns a string containing 4*s whitespaces."""

        return " " * (s*4)
