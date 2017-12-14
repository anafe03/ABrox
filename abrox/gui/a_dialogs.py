from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from collections import OrderedDict
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

    def __init__(self, internalModel, parent=None):
        super(AFixParameterDialog, self).__init__(parent)

        self._internalModel = internalModel
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

        # Get an list of 2-tuples (key, value) of checkboxes
        fixedParams = [spin.keyValue() for spin in self._spinBoxes]
        # Add to internal model
        self._internalModel.addFixedParameters(fixedParams)
        # Close dialog
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


class ARejectionSettingsDialog(QDialog):
    """
    Represents a pop-up for specifying the settings
    of the rejection algorithm.
    """

    def __init__(self, internalModel, parent=None):
        super(ARejectionSettingsDialog, self).__init__(parent)

        self._internalModel = internalModel
        self._simEntry = [
            QLabel('Number of simulations:'),
            ASettingEntry(self._internalModel, 'simulations')
        ]
        self._settingsEntries = {
            'keep': (QLabel('Keep:'), ASettingEntry(self._internalModel, 'keep')),
            'threshold': (QLabel('Threshold:'), ASettingEntry(self._internalModel, 'threshold')),
            'cv': (QLabel('Cross Validation Samples:'), ASettingEntry(self._internalModel, 'cv'))
        }
        self._refTableWidget = ARefTableDir(internalModel)
        self._initDialog(QVBoxLayout())

    def _initDialog(self, dialogLayout):
        """Configures dialog."""

        self.setWindowTitle('Rejection Settings')

        refTableBox = self._createReferenceTableSettingsBox()
        settingsBox = self._createAlgorithmSettingsBox()
        buttonsBox = createDialogYesNoButtons(self._onOk, self._onCancel)

        dialogLayout.addWidget(refTableBox)
        dialogLayout.addWidget(settingsBox)
        dialogLayout.addWidget(buttonsBox)
        self.setLayout(dialogLayout)
        self.adjustSize()

    def _createReferenceTableSettingsBox(self):
        """Creates a reference table."""

        refGroupBox = QGroupBox('Reference Table Settings')
        refGroupBoxLayout = QGridLayout()

        # Add number of simulations label and entry
        refGroupBoxLayout.addWidget(self._simEntry[0], 0, 0, 1, 1)
        refGroupBoxLayout.addWidget(self._simEntry[1], 0, 1, 1, 1)

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
            specs = self._internalModel.algorithmDefaultSpecs('rj')

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
        rejectionBoxLayout.addWidget(autoCheck, 1, 2)

        # Add cross validation checkbutton
        cvCheck = QCheckBox()
        cvCheck.setText('No CV')
        if specs['cv'] is None:
            autoCheck.setChecked(True)
            self._toggleSetting(False, 'cv')

        cvCheck.toggled.connect(self._onCv)
        rejectionBoxLayout.addWidget(cvCheck, 2, 2)

        rejectionBox.setLayout(rejectionBoxLayout)
        return rejectionBox

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

    def _onAuto(self, checked):
        """Activated when user toggles the automatic threshold setting"""

        self._toggleSetting(checked, 'threshold')

    def _onCv(self, checked):
        """Activated when user decides to click the no cv checkbutton."""

        self._toggleSetting(checked, 'cv')

    def _collect(self):
        """Collects values from entries and updates internal model."""

        methodSpecs = self._internalModel.algorithmDefaultSpecs('rj')
        # Update values (order does not matter, since methodSpecs is an orderedDict
        for key in self._settingsEntries.keys():
            methodSpecs[key] = self._settingsEntries[key][1].value()
        refTableSpecs = {
            'simulations': self._simEntry[1].value()
            'extref':
        }

    def _onOk(self):
        """Called when user presses ok. Update method settings."""

        # Update model

        self.close()

    def _onCancel(self):
        """Called when user presses cancel. Accepted stays False."""
        self.close()


class ASettingEntry(QDoubleSpinBox):
    """Derives from a basic line edit to include a key, corresponding to the model setting."""

    def __init__(self, internalModel, key, parent=None):
        super(ASettingEntry, self).__init__(parent)

        self._internalModel = internalModel
        self._key = key

        # Adjust spinbox range
        self._configureRange()

    def _configureRange(self):
        """Sets the range of the spinbox."""

        if self._key == 'keep':
            # Keep settings
            self.setRange(0, 1e10)
            self.setDecimals(0)

        elif self._key == 'threshold':
            # Threshold settings
            self.setSingleStep(0.1)
            self.setDecimals(3)
            self.setRange(0.0, 1.0)

        elif self._key == 'simulations':
            # N simulations settings
            self.setRange(0, 1e10)
            self.setSingleStep(10)
            self.setDecimals(0)
        elif self._key == 'cv':
            # Cross-validation settings
            self.setRange(0, 1e10)
            self.setSingleStep(10)
            self.setDecimals(0)


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
        self._path.setPlaceholderText('Ref. table location...')
        # TODO - add path, if existing
        self._path.textChanged.connect(self._onEdit)

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
            # Update entry
            self._path.setText(loadedFileName[0])
            # Update internal model
            self._internalModel.changeSetting('ref_table', {
                            'simulations': None,
                            'extref': loadedFileName[0]})
            # Modify save flag
            tracksave.saved = False

    def _onEdit(self, text):
        """Triggered when user types into dir edit."""

        # Update internal model with typed stuff
        self._internalModel.changeSetting('ref_table', {
                            'simulations': None,
                            'extref': text})
        # Modify save flag
        tracksave.saved = False

