from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


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
        buttonsBox = self._createButtonsBox()

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

    def _createButtonsBox(self):
        """Creates the no and cancel buttons."""

        # Create OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   Qt.Horizontal)
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self._onCancel)
        return buttons

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
        buttonsBox = self._createButtonsBox()

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

    def _createButtonsBox(self):
        """Creates the no and cancel buttons."""

        # Create OK, Cancel, and Reset buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset,
            Qt.Horizontal)
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self._onCancel)
        buttons.button(QDialogButtonBox.Reset).clicked.connect(self._onReset)
        return buttons

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
