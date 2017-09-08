from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pandas as pd


class ALoadDataDialog(QDialog):
    """Represents a pop-up for loading data response."""

    def __init__(self, fileName, parent=None):
        super(ALoadDataDialog, self).__init__(parent)

        self.fileName = fileName
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

        # get checked button type
        sep = self._buttons.checkedButton().text()

        try:
            if sep == 'Tab':
                data = pd.read_csv(self.fileName, delimiter='\t', header=0)
            elif sep == 'Whitespace':
                data = pd.read_csv(self.fileName, delim_whitespace=True, header=0)
            elif sep == 'Semicolon':
                data = pd.read_csv(self.fileName, delimiter=';', header=0)
            elif sep == 'Comma':
                data = pd.read_csv(self.fileName, delimiter=',', header=0)
            else:
                data = pd.read_csv(self.fileName, delimiter=self._otherEntry.text(), header=0)

            self.data = data
            self.accepted = True
            self.close()

        except IOError as e:
            QMessageBox.critical(self, 'Could not load file...',
                                 str(e), QMessageBox.Ok)

    def _onCancel(self):
        """Called when user presses cancel. Accepted stays False."""

        self.close()


class ACheckButton(QCheckBox):

    def __init__(self, delimType, parent):
        super(ACheckButton, self).__init__(delimType, parent)

        self.delimType = delimType
