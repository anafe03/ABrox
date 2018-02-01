from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import abc
from abrox.gui.a_utils import createDialogYesNoButtons, createButton
from abrox.gui import tracksave


class ALoadDataDialog(QDialog):
    """Represents a pop-up for obtaining the data delimiter."""

    def __init__(self, fileName, internalModel, parent=None):
        super(ALoadDataDialog, self).__init__(parent)

        self.fileName = fileName
        self._internalModel = internalModel
        self._buttons = QButtonGroup(self)
        self.data = None
        self.accepted = False

        self._initDialog(QVBoxLayout())

    def _initDialog(self, dialogLayout):
        """Configures dialog."""

        # Set title
        self.setWindowTitle('Data Information')

        # Create a group box and buttons box
        groupBox = self._createGroupBox()
        buttonsBox = createDialogYesNoButtons(self._onOk, self._onCancel)

        # Configure layout
        dialogLayout.addWidget(groupBox)
        dialogLayout.addWidget(buttonsBox)
        self.setLayout(dialogLayout)
        self.adjustSize()

    def _createGroupBox(self):
        """Create the checkboxes."""

        # Create group box
        buttonGroup = QGroupBox('Delimiter')
        boxLayout = QGridLayout()
        self._buttons.setExclusive(True)

        # Define delimiter types
        types = ['Tab', 'Whitespace', 'Semicolon', 'Comma']

        # Add checkbuttons to group
        for idx, delim in enumerate(types):
            check = QCheckBox(delim)
            if idx == 0:
                check.setChecked(True)
            boxLayout.addWidget(check, idx, 0, 1, 2, Qt.AlignBottom)
            self._buttons.addButton(check)

        # Add other checkbutton and entry
        check = QCheckBox('Other:')
        self._buttons.addButton(check)
        self._otherEntry = QLineEdit()
        self._otherEntry.setMaximumWidth(60)
        boxLayout.addWidget(check, idx+1, 0, 1, 1, Qt.AlignTop)
        boxLayout.addWidget(self._otherEntry, idx+1, 1, 1, 1, Qt.AlignBottom)

        # Add layout to group
        buttonGroup.setLayout(boxLayout)

        # Return the group
        return buttonGroup

    def _onOk(self):
        """Load data using pandas."""

        # Get checked button type
        sepText = self._buttons.checkedButton().text()

        # Check type of delimiter
        if sepText == 'Tab':
            delimiter = '\t'
        elif sepText == 'Whitespace':
            delimiter = r'\s*'
        elif sepText == 'Semicolon':
            delimiter = ';'
        elif sepText == 'Comma':
            delimiter = ','
        else:
            delimiter = self._otherEntry.text()

        # Update model
        self._internalModel.addDataFileAndDelimiter(self.fileName, delimiter)
        self.accepted = True
        self.close()

    def _onCancel(self):
        """Called when user presses cancel. Accepted stays False."""

        self.close()


class AFixParameterDialog(QDialog):
    """
    Represents a pop-up for fixing parameters.
    Assumes that a model index is available in the internal model.
    """

    def __init__(self, internalModel, outputConsole, parent=None):
        super(AFixParameterDialog, self).__init__(parent)

        self._internalModel = internalModel
        self._outputConsole = outputConsole
        self._spinBoxes = []
        self._initDialog(QVBoxLayout())

    def _initDialog(self, dialogLayout):
        """Configures dialog."""

        # Set title
        self.setWindowTitle('Fix Parameters...')

        # Create a group box and buttons box
        groupBox = self._createGroupBox()
        buttonsBox = createDialogYesNoButtons(self._onOk, self._onCancel, self._onReset)

        # Configure layout
        dialogLayout.addWidget(groupBox)
        dialogLayout.addWidget(buttonsBox)
        self.setLayout(dialogLayout)
        self.adjustSize()

    def _createGroupBox(self):
        """Create the labels and entries according to internal model."""

        # Get selected model from internalModel
        model = self._internalModel.selectedModelForTest()

        # Create group box
        buttonGroup = QGroupBox('Fix Parameters of ' + model.name)
        boxLayout = QGridLayout()

        # Check if model has priors
        if model.hasPriors():
            # Add first row (header)
            param = QLabel('Parameter')
            font = param.font()
            font.setBold(True)
            param.setFont(font)
            value = QLabel('Value')
            value.setFont(font)
            boxLayout.addWidget(param, 0, 0, 1, 1)
            boxLayout.addWidget(value, 0, 1, 1, 1, Qt.AlignRight)

            # Create entries according to model priors
            for idx, prior in enumerate(model):
                # Each prior is its own dict, idx + 1, since we have a header

                # Add label (parameter name)
                boxLayout.addWidget(QLabel(list(prior.keys())[0]), idx+1, 0, 1, 1)

                # Add spinbox to list and layout
                smartSpin = ASmartSpinBox(list(prior.keys())[0])
                self._spinBoxes.append(smartSpin)
                boxLayout.addWidget(smartSpin, idx+1, 1, 1, 1)
        else:
            # Model has no priors, display informative text and modify flag
            boxLayout.addWidget(QLabel('Model has no priors...'), 1, 0, 1, 1)

        # Add layout to group
        boxLayout.setContentsMargins(5, 20, 5, 10)
        buttonGroup.setLayout(boxLayout)

        # Return the group
        return buttonGroup

    def _onOk(self):
        """Add fixed parameters to internal model and close."""

        # Get a list of 2-tuples (key, value) of checkboxes
        fixedParams = [spin.keyValue() for spin in self._spinBoxes]
        self._internalModel.addFixedParameters(fixedParams)
        tracksave.saved = False
        self._outputConsole.write('Following parameters of model <strong>{}</strong> fixed:'
                                  .format(self._internalModel.selectedModelForTest().name))
        [self._outputConsole.write('Parameter <strong>{}</strong> set to <strong>{}</strong>'
                                   .format(k, v)) for k, v in fixedParams]
        self.close()

    def _onCancel(self):
        """Called when user presses cancel. Accepted stays False."""
        self.close()

    def _onReset(self):
        """Called on reset press. Resets the dict of fixed parameters."""
        self._internalModel.addFixedParameters(list())
        self.close()


class ACheckButton(QCheckBox):

    def __init__(self, delimType, parent):
        super(ACheckButton, self).__init__(delimType, parent)

        self.delimType = delimType


class ASmartSpinBox(QDoubleSpinBox):
    """Represents a spinbox which holds the key of its parameter."""

    def __init__(self, key, parent=None):
        super(ASmartSpinBox, self).__init__(parent)

        self.key = key
        self.setRange(-1e10, 1e10)

    def keyValue(self):
        """Returns a key: value tuple."""

        return self.key, self.value()


class ASettingsDialog(QDialog):
    """
    Represents an abstract pop-up for specifying the settings
    of an algorithm algorithm. Concerete instances of this class
    should implement the two abstract methods specified below.
    """

    def __init__(self, internalModel, outputConsole, parent=None):
        super(ASettingsDialog, self).__init__(parent)

        self._internalModel = internalModel
        self._outputConsole = outputConsole
        self._refTableWidget = ARefTableDir(internalModel)
        self._simEntry = [
            QLabel('Number of simulations:'),
            ASettingEntry(self._internalModel, 'simulations', True)
        ]

    def _createReferenceTableSettingsBox(self):
        """Creates a reference table."""

        refGroupBox = QGroupBox('Reference Table Settings')
        refGroupBoxLayout = QGridLayout()

        # Add number of simulations label and entry
        refGroupBoxLayout.addWidget(self._simEntry[0], 0, 0, 1, 1)
        refGroupBoxLayout.addWidget(self._simEntry[1], 0, 1, 1, 1)

        self._simEntry[1].setValue(self._internalModel.simulations())

        useExtCheck = QCheckBox("Use external reference table")
        refGroupBoxLayout.addWidget(useExtCheck, 1, 0, 1, 1)

        # Toggle, if specified in model
        if self._internalModel.externalReference() is not None:
            useExtCheck.setChecked(True)
            self._toggleExt(True)
        else:
            useExtCheck.setChecked(False)
            self._toggleExt(False)

        # Connect toggle event to method
        useExtCheck.toggled.connect(self._onExt)

        # Add file selector entry to layout
        refGroupBoxLayout.addWidget(self._refTableWidget, 2, 0, 1, 2)
        refGroupBox.setLayout(refGroupBoxLayout)
        return refGroupBox

    @abc.abstractmethod
    def _createAlgorithmSettingsBox(self):
        """Lays out the specific settings of the algorithm."""
        raise NotImplementedError("This method needs to be implemented.")

    @abc.abstractmethod
    def _algorithm(self):
        """Returns the name of the algorithm (rejection, mcmc...)"""
        raise NotImplementedError("This method needs to be implemented.")

    def _initDialog(self, dialogLayout):
        """Configures dialog."""

        refTableBox = self._createReferenceTableSettingsBox()
        settingsBox = self._createAlgorithmSettingsBox()
        buttonsBox = createDialogYesNoButtons(self._onOk, self._onCancel)

        dialogLayout.addWidget(refTableBox)
        dialogLayout.addWidget(settingsBox)
        dialogLayout.addWidget(buttonsBox)
        self.setLayout(dialogLayout)
        self.adjustSize()

    def _onOk(self):
        """Called when user presses ok. Update method settings."""

        if not self._refTableWidget.val() and not self._simEntry[1].isEnabled():
            # User has not specified path to external
            self._refTableWidget.warn()
            return
        method, ref = self._collect()
        self._internalModel.addMethod(method)
        self._internalModel.addRefTable(ref)
        tracksave.saved = False
        self._outputConsole.write('Method changed to {}.'.format(self._name))
        self.close()

    def _onCancel(self):
        """Called when user presses cancel. Accepted stays False."""
        self.close()

    def _toggleExt(self, enabled):
        """A helper function to toggle selected dir or not."""

        self._refTableWidget.setEnabled(enabled)
        self._simEntry[0].setEnabled(not enabled)
        self._simEntry[1].setEnabled(not enabled)

    def _toggleSetting(self, enabled, key):
        """A helper to toggle settings on/off."""

        self._settingsEntries[key][0].setEnabled(not enabled)
        self._settingsEntries[key][1].setEnabled(not enabled)

    def _onExt(self, checked):
        """Activated when user decides to add external reference."""

        self._toggleExt(checked)

    def _collect(self):
        """Collects values from entries and updates internal model."""

        methodSpecs = self._internalModel.algorithmDefaultSpecs(self._algorithm())
        # Update values (order does not matter, since methodSpecs is an orderedDict
        for key in self._settingsEntries.keys():
            if not self._settingsEntries[key][1].isEnabled():
                # User has deselected, value is None
                methodSpecs[key] = None
            else:
                # User has selected, use given value
                methodSpecs[key] = self._settingsEntries[key][1].val()

        refTableSpecs = {
            'simulations': int(self._simEntry[1].val()),
            'extref': self._refTableWidget.val()
        }
        method = {
            'algorithm': self._algorithm(),
            'specs': methodSpecs
        }
        return method, refTableSpecs


class ARejectionSettingsDialog(ASettingsDialog):
    """
    Represents a pop-up for specifying the settings
    of the rejection algorithm.
    """

    def __init__(self, internalModel, outputConsole, parent=None):
        super(ARejectionSettingsDialog, self).__init__(internalModel, outputConsole, parent)

        self._name = 'Rejection'
        self.setWindowTitle(self._name + ' Settings')
        self._settingsEntries = {
            'keep': (QLabel('Keep:'), ASettingEntry(self._internalModel, 'keep', True)),
            'threshold': (QLabel('Threshold:'), ASettingEntry(self._internalModel, 'threshold')),
            'cv': (QLabel('Cross Validation Samples:'), ASettingEntry(self._internalModel, 'cv', True))
        }
        self._initDialog(QVBoxLayout())

    def _createAlgorithmSettingsBox(self):
        """Called after reference table settings created."""

        rejectionBox = QGroupBox('Algorithm Settings')
        rejectionBoxLayout = QGridLayout()

        # Use list in order to show in order
        keys = ['keep', 'threshold', 'cv']

        if self._internalModel.algorithm() == "rejection":
            # Show settings already selected
            specs = self._internalModel.algorithmSpecs()
        else:
            # Show default settings
            specs = self._internalModel.algorithmDefaultSpecs('rejection')

        for idx, key in enumerate(keys):
            # Add label and entry
            rejectionBoxLayout.addWidget(self._settingsEntries[key][0], idx, 0, 1, 1)
            rejectionBoxLayout.addWidget(self._settingsEntries[key][1], idx, 1, 1, 1)

            # Set settings value according to model
            if specs[key] is not None:
                self._settingsEntries[key][1].setValue(specs[key])

        # Add automatic threshold checkbutton
        autoCheck = QCheckBox()
        autoCheck.setText('Automatic')

        if specs['threshold'] is None:
            autoCheck.setChecked(True)
            self._toggleSetting(True, 'threshold')
        autoCheck.toggled.connect(self._onAuto)
        rejectionBoxLayout.addWidget(autoCheck, keys.index('threshold'), 2)

        # Add cross validation checkbutton
        cvCheck = QCheckBox()
        cvCheck.setText('No CV')
        if specs['cv'] is None:
            cvCheck.setChecked(True)
            self._toggleSetting(True, 'cv')

        cvCheck.toggled.connect(self._onCv)
        rejectionBoxLayout.addWidget(cvCheck, keys.index('cv'), 2)

        rejectionBox.setLayout(rejectionBoxLayout)
        return rejectionBox

    def _algorithm(self):
        return "rejection"

    def _onAuto(self, checked):
        """Activated when user toggles the automatic threshold setting"""

        self._toggleSetting(checked, 'threshold')

    def _onCv(self, checked):
        """Activated when user decides to click the no cv checkbutton."""

        self._toggleSetting(checked, 'cv')


class AMCMCSettingsDialog(ASettingsDialog):
    """
    Represents a pop-up for specifying the settings
    of the MCMC algorithm.
    """

    def __init__(self, internalModel, outputConsole, parent=None):
        super(AMCMCSettingsDialog, self).__init__(internalModel, outputConsole, parent)

        self._name = 'MCMC'
        self.setWindowTitle(self._name + ' Settings')
        self._settingsEntries = {
            'keep': (QLabel('Keep:'), ASettingEntry(self._internalModel, 'keep', True)),
            'threshold': (QLabel('Threshold:'), ASettingEntry(self._internalModel, 'threshold')),
            'chl': (QLabel('Chain Length:'), ASettingEntry(self._internalModel, 'chl', True)),
            'burn': (QLabel('Burn-In'), ASettingEntry(self._internalModel, 'burn', True)),
            'thin': (QLabel('Thinning'), ASettingEntry(self._internalModel, 'thin', True)),
            'proposal': (QLabel('Proposal Distribution:'), QSpinBox()),
            'start': (QLabel('Optimizer:'), QSpinBox()),
        }
        self._initDialog(QVBoxLayout())

    def _createAlgorithmSettingsBox(self):
        """Called after reference table settings created."""

        mcmcBox = QGroupBox('Algorithm Settings')
        mcmcBoxLayout = QGridLayout()

        # Use list in order to show in order
        keys = ['keep', 'threshold', 'chl', 'burn', 'thin', 'proposal', 'start']

        if self._internalModel.algorithm() == "mcmc":
            # Show settings already selected
            specs = self._internalModel.algorithmSpecs()
        else:
            # Show default settings
            specs = self._internalModel.algorithmDefaultSpecs('mcmc')

        for idx, key in enumerate(keys):
            # Add label and entry
            mcmcBoxLayout.addWidget(self._settingsEntries[key][0], idx, 0, 1, 1)
            mcmcBoxLayout.addWidget(self._settingsEntries[key][1], idx, 1, 1, 1)

            # Set settings value according to model
            if specs[key] is not None:
                self._settingsEntries[key][1].setValue(specs[key])

        # Add automatic threshold checkbutton
        autoCheck = QCheckBox()
        autoCheck.setText('Automatic')

        if specs['threshold'] is None:
            autoCheck.setChecked(True)
            self._toggleSetting(True, 'threshold')
        autoCheck.toggled.connect(self._onAuto)
        mcmcBoxLayout.addWidget(autoCheck, keys.index('threshold'), 2)

        # Add proposal checkbutton
        proposalCheck = QCheckBox()
        proposalCheck.setText('Automatic')

        if specs['proposal'] is None:
            proposalCheck.setChecked(True)
            self._toggleSetting(True, 'proposal')
        # TODO -unblock
        proposalCheck.setCheckable(False)
        proposalCheck.toggled.connect(self._onProposal)
        mcmcBoxLayout.addWidget(proposalCheck, keys.index('proposal'), 2)

        # Add start checkbutton
        startCheck = QCheckBox()
        startCheck.setText('Automatic')

        if specs['start'] is None:
            proposalCheck.setChecked(True)
            self._toggleSetting(True, 'start')
        # TODO -unblock
        startCheck.setCheckable(False)
        startCheck.toggled.connect(self._onStart)
        mcmcBoxLayout.addWidget(startCheck, keys.index('start'), 2)

        mcmcBox.setLayout(mcmcBoxLayout)
        return mcmcBox

    def _algorithm(self):
        return "mcmc"

    def _onAuto(self, checked):
        """Activated when user toggles the automatic threshold setting"""

        self._toggleSetting(checked, 'threshold')

    def _onProposal(self, checked):
        """Activated when user toggles the automatic threshold setting"""

        # TODO - add options, not it does nothing
        pass

    def _onStart(self, checked):
        """Activated when user toggles the automatic threshold setting"""

        # TODO - add options, not it does nothing
        pass


class ARandomForestSettingsDialog(ASettingsDialog):
    """
    Represents a pop-up for specifying the settings
    of the Random Forest ABC algorithm.
    """

    def __init__(self, internalModel, outputConsole, parent=None):
        super(ARandomForestSettingsDialog, self).__init__(internalModel, outputConsole, parent)

        self._name = 'Random Forest'
        self.setWindowTitle(self._name + ' Settings')
        self._settingsEntries = {
            'n_estimators': (QLabel('Number of Trees:'),
                             ASettingEntry(self._internalModel, 'ntree', True)),
            'max_depth': (QLabel('Maximum Depth:'),
                          ASettingEntry(self._internalModel, 'mdepth', True)),
            'min_samples_split': (QLabel('Minimum Samples per Split'),
                                  ASettingEntry(self._internalModel, 'msplit', True)),
            'min_samples_leaf': (QLabel('Minimum Samples perLeaf:'),
                                 ASettingEntry(self._internalModel, 'mleaf', True)),
            'criterion': (QLabel('Criterion:'),
                          AComboBox(['gini', 'entropy']))
        }
        self._initDialog(QVBoxLayout())

    def _createAlgorithmSettingsBox(self):
        """Called after reference table settings created."""

        rfBox = QGroupBox('Algorithm Settings')
        rfBoxLayout = QGridLayout()

        keys = ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'criterion']

        if self._internalModel.algorithm() == "randomforest":
            # Show settings already selected
            specs = self._internalModel.algorithmSpecs()
        else:
            # Show default settings
            specs = self._internalModel.algorithmDefaultSpecs('randomforest')

        for idx, key in enumerate(keys):
            # Add label and entry
            rfBoxLayout.addWidget(self._settingsEntries[key][0], idx, 0, 1, 1)
            rfBoxLayout.addWidget(self._settingsEntries[key][1], idx, 1, 1, 1)

            # Set settings value according to model
            if specs[key] is not None:
                self._settingsEntries[key][1].setValue(specs[key])

        # Add auto max depth checkbutton
        maxDepthCheck = QCheckBox()
        maxDepthCheck.setText('Automatic')

        if specs['max_depth'] is None:
            maxDepthCheck.setChecked(True)
            self._toggleSetting(True, 'max_depth')
        maxDepthCheck.toggled.connect(self._onMaxDepth)
        rfBoxLayout.addWidget(maxDepthCheck, keys.index('max_depth'), 2)

        rfBox.setLayout(rfBoxLayout)
        return rfBox

    def _algorithm(self):
        return "randomforest"

    def _onMaxDepth(self, checked):
        """Activated when user toggles the max depth automatic setting"""

        self._toggleSetting(checked, 'max_depth')


class ASettingEntry(QDoubleSpinBox):
    """Derives from a basic line edit to include a key, corresponding to the model setting."""

    def __init__(self, internalModel, key, integer=False, parent=None):
        super(ASettingEntry, self).__init__(parent)

        self._internalModel = internalModel
        self._key = key
        self._integer = integer

        # Adjust spinbox range
        self._configureRange()

    def _configureRange(self):
        """Sets the range of the spinbox."""

        if self._key == 'keep':
            self._customize([1, 1e10], 10, 0)

        elif self._key == 'threshold':
            self._customize([0.001, 1.0], 0.1, 3)

        elif self._key == 'simulations':
            self._customize([1, 1e10], 100, 0)

        elif self._key == 'cv':
            self._customize([1, 1e10], 10, 0)

        elif self._key == 'chl':
            self._customize([1, 1e10], 1000, 0)

        elif self._key == 'burn':
            self._customize([0, 1e10], 10, 0)

        elif self._key == 'thin':
            self._customize([0, 1e10], 10, 0)

        elif self._key == 'mdepth':
            self._customize([1, 1e10], 1, 0)

        elif self._key == 'msplit':
            self._customize([1, 1e10], 1, 0)

        elif self._key == 'mleaf':
            self._customize([1, 1e10], 1, 0)

        elif self._key == 'ntree':
            self._customize([1, 1e10], 10, 0)

    def _customize(self, fromTo=None, step=None, decimal=None):
        self.setRange(*fromTo)
        self.setSingleStep(step)
        self.setDecimals(decimal)

    def val(self):
        if self._integer:
            return int(self.value())
        return self.value()


class ARefTableDir(QWidget):
    """Reference table file for specifying the location of the ref table."""

    def __init__(self, internalModel, parent=None):
        super(ARefTableDir, self).__init__(parent)

        self._internalModel = internalModel
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Creates and sets the layout."""

        # Create edit for path
        self._path = QLineEdit()
        self._path.setPlaceholderText('Reference table location...')
        if self._internalModel.externalReference():
            self._path.setText(self._internalModel.externalReference())

        # Create button for dir
        self._button = createButton("", './icons/load.png', 'Select reference table file...',
                                    self._onOpen, Qt.NoFocus, True, True)

        # Add widgets to layout
        layout.addWidget(self._button)
        layout.addWidget(self._path)
        layout.setSpacing(0)
        self.setLayout(layout)

    def _onOpen(self):
        """Opens up a file dialog for choosing an output folder."""

        # Create file dialog
        loadedFileName = QFileDialog.getOpenFileName(self, 'Select reference table file...',
                                                     '', "Text Files (*.csv *.txt)")

        # If user has selected something
        if loadedFileName[0]:
            # Update entry and don't update model, since
            # we need to make sure dialog is accepted
            self._path.setText(loadedFileName[0])

    def val(self):
        return self._path.text() if self._path.text() else None

    def warn(self):
        QToolTip.showText(self.mapToGlobal(self._path.rect().bottomLeft()),
                          'Please insert a valid path',
                          None)


class AComboBox(QComboBox):

    def __init__(self, comboList, parent=None):
        super(AComboBox, self).__init__(parent)

        for i, item in enumerate(comboList):
            self.insertItem(i, item.capitalize())

    def val(self):
        return self.currentText().lower()

    def setValue(self, val):
        self.setCurrentText(val.upper())