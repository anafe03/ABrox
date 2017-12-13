from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
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
        self._refTableWidget = ARefTableDir(internalModel)
        self._initDialog(QVBoxLayout())

    def _initDialog(self, dialogLayout):
        """Configures dialog."""

        # Set title
        self.setWindowTitle('Rejection settings')

        # Create a group box and buttons box
        refTableBox = self._createReferenceTableSettingsBox()
        buttonsBox = createDialogYesNoButtons(self._onOk, self._onCancel)

        # Configure layout
        dialogLayout.addWidget(refTableBox)
        dialogLayout.addWidget(buttonsBox)
        self.setLayout(dialogLayout)
        self.adjustSize()

    def _createReferenceTableSettingsBox(self):
        """Creates a reference table."""

        # Create objective group box
        refGroupBox = QGroupBox('Reference Table Settings')
        refGroupBoxLayout = QGridLayout()

        # Add number of simulations label and entry
        refGroupBoxLayout.addWidget(self._simEntry[0], 0, 0, 1, 1)
        refGroupBoxLayout.addWidget(self._simEntry[1], 0, 1, 1, 1)

        # Add use external reference table layout and modify external selector
        useExtRadio = QCheckBox("Use external reference table")
        refGroupBoxLayout.addWidget(useExtRadio, 1, 0, 1, 1)

        # Toggle, if specified in model
        if self._internalModel.externalReference() is not None:
            useExtRadio.setChecked(True)
            self._toggleExt(True)
        else:
            useExtRadio.setChecked(False)
            self._toggleExt(False)

        # Connect toggle event to method
        useExtRadio.toggled.connect(self._onRadio)

        # Add file selector entry to layout
        refGroupBoxLayout.addWidget(self._refTableWidget, 2, 0, 1, 2)
        refGroupBox.setLayout(refGroupBoxLayout)
        return refGroupBox

    def _toggleExt(self, enabled):
        """A helper function to toggle selected dir or not."""

        self._refTableWidget.setEnabled(enabled)
        self._simEntry[0].setEnabled(not enabled)
        self._simEntry[1].setEnabled(not enabled)

    def _createGroupBox(self):
        """Creates a box with parameters."""

        # Create rejection settings pane
        rejectionBox = QWidget()
        rejectionBoxLayout = QGridLayout()

        # Use this for rejection
        labels = [('Number of simulations:', 'simulations'),
                  ('Threshold:', 'threshold'),
                  ('Keep:', 'keep'),
                  ('Cross Validation:', 'cv')]

        for idx, label in enumerate(labels):
            labelName = labels[idx][0]
            key = labels[idx][1]

            rejectionBoxLayout.addWidget(QLabel(labelName, self), idx, 0, 1, 1)

            # Create entry and add to layout and dict
            entry = ASettingEntry(self._internalModel, key)
            rejectionBoxLayout.addWidget(entry, idx, 1, 1, 1)
            self._settingEntries[key] = entry

        # Add automatic threshold check button
        self._autoCheck = QCheckBox()
        self._autoCheck.setText('Automatic')
        rejectionBoxLayout.addWidget(self._autoCheck, 1, 2)

        # Set layout and return ready box
        rejectionBox.setLayout(rejectionBoxLayout)
        return rejectionBox

    def _onRadio(self, checked):
        """Activated when user decides to add external reference."""

        if checked:
            self._toggleExt(True)
        else:
            self._toggleExt(False)

    def _onOk(self):
        """Called when user presses ok. Update method settings."""

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

        # Set value from model
        #self.setValue(self._internalModel['settings'][key])
        #self.valueChanged.connect(self._onValueChanged)

    def _configureRange(self):
        """Sets the range of the spinbox."""

        self.setDecimals(3)
        self.setSingleStep(0.1)
        # Percentile settings
        if self._key == 'keep':
            self.setRange(0, 1e10)
            self.setDecimals(0)
        # Threshold settings
        if self._key == 'threshold':
            self.setRange(0.0, 1e10)

        # N simulations settings
        if self._key == 'simulations':
            self.setRange(0, 1e10)
            self.setSingleStep(10)
            self.setDecimals(0)
        # Cross-validation settings
        if self._key == 'cv':
            self.setRange(0, 1e6)
            self.setSingleStep(10)
            self.setDecimals(0)

    def _onValueChanged(self, val):
        """Triggered when user changes the value fo the setting."""
        pass


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

