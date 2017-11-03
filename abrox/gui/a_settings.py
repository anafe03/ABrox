from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pickle
from abrox.gui.a_process_manager import AProcessManager
from abrox.gui.a_dialogs import AFixParameterDialog
from abrox.gui.a_script_creator import AScriptCreator
from abrox.gui.a_utils import createButton
from abrox.gui import tracksave


class ASettingsWindow(QFrame):
    """Main container for the output settings and run."""
    def __init__(self, internalModel, console, outputConsole, parent=None):
        super(ASettingsWindow, self).__init__(parent)

        self._internalModel = internalModel
        self._console = console
        self._compSettingsFrame = AComputationSettingsFrame(internalModel, console)
        self._modelTestFrame = ARunFrame(internalModel, console, outputConsole)
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Lays out main components of the frame."""

        self.setFrameStyle(QFrame.Panel)

        layout.addWidget(self._compSettingsFrame)
        layout.addWidget(self._modelTestFrame)
        layout.setStretchFactor(self._compSettingsFrame, 1)
        layout.setStretchFactor(self._modelTestFrame, 2)

        self.setLayout(layout)


class AComputationSettingsFrame(QScrollArea):
    """Main container for settings and run."""
    def __init__(self, internalModel, console, parent=None):
        super(AComputationSettingsFrame, self).__init__(parent)

        # Private attributes
        self._internalModel = internalModel
        self._console = console
        self._output = AOuputDir(internalModel)
        self._comboWidget = QWidget()
        self._settingEntries = dict()
        self._hyperparametersFrame = QStackedWidget()

        # Method buttons
        self._methodButtons = {"group": QButtonGroup(),
                               "buttons": {
                                   "rj": QRadioButton("Rejection"),
                                   "rf": QRadioButton("Random Forest"),
                                   "mcmc": QRadioButton("MCMC")}
                               }
        # Objective buttons
        self._objectiveButtons = {"group": QButtonGroup(),
                                  "buttons": {
                                     "pe": QRadioButton("Parameter Estimation"),
                                     "mc": QRadioButton("Model Comparison")}
                               }

        self._configureLayout(QVBoxLayout())

    def _configureLayout(self, layout):
        """Lays out main components of the frame."""

        generalGroupBox = self._generalSettingsGroup()
        modelTestGroupBox = self._modelTestSettingsGroup()

        layout.addWidget(generalGroupBox)
        layout.addWidget(modelTestGroupBox)
        layout.addStretch(1)

        # Inner widget of scrollarea
        content = QWidget()
        content.setLayout(layout)

        # Place inner widget inside the scrollable area
        self.setWidget(content)
        self.setWidgetResizable(True)

    def _generalSettingsGroup(self):
        """Create and returns the general settings group box."""

        # Create a group box
        groupBox = QGroupBox('General Settings')
        groupBoxLayout = QVBoxLayout()

        # Define a container to hold the relevant settings
        # for objective, method and settings panes
        containerLayout = QGridLayout()
        container = QWidget()

        # Create components
        objectiveBox = self._createObjectiveBox()
        methodBox = self._createMethodBox()
        hyperBox = self._createHyperParamsBox()

        # Lay out components
        containerLayout.addWidget(objectiveBox, 0, 0, 1, 1)
        containerLayout.addWidget(methodBox, 0, 1, 1, 1)
        containerLayout.addWidget(hyperBox, 1, 0, 1, 2)

        # # Lay out container
        container.setLayout(containerLayout)
        groupBoxLayout.addWidget(self._output)
        groupBoxLayout.addWidget(container)
        groupBox.setLayout(groupBoxLayout)

        return groupBox

    def _createObjectiveBox(self):
        """Returns the ready objective group box."""

        # Create objective group box
        objectiveGroupBox = QGroupBox('Objective')
        objectiveGroupBoxLayout = QVBoxLayout()

        # Add radio buttons to group and layout
        for button in self._objectiveButtons["buttons"].values():
            self._objectiveButtons["group"].addButton(button)
            objectiveGroupBoxLayout.addWidget(button)
        self._objectiveButtons["group"].buttonClicked.connect(self._onObjective)

        objectiveGroupBox.setLayout(objectiveGroupBoxLayout)
        return objectiveGroupBox

    def _createMethodBox(self):
        """Returns the ready method group box."""

        # Create group box
        methodGroupBox = QGroupBox('Method')
        methodGroupBoxLayout = QVBoxLayout()

        # Add radio buttons to group and layout
        for button in self._methodButtons["buttons"].values():
            self._methodButtons["group"].addButton(button)
            methodGroupBoxLayout.addWidget(button)
        self._methodButtons["group"].buttonClicked.connect(self._onMethod)

        methodGroupBox.setLayout(methodGroupBoxLayout)
        return methodGroupBox

    def _createHyperParamsBox(self):
        """Returns the ready hyper parameters box."""

        # Create groupbox and subboxes
        hyperParamsBox = QGroupBox("Hyperparameters")
        hyperParamsBoxLayout = QVBoxLayout()
        rejectionBox = self._createRejectionBox()
        mcmcBox = self._createMCMCBox()

        # Add settings boxes to stacked widget
        self._hyperparametersFrame.addWidget(rejectionBox)
        self._hyperparametersFrame.addWidget(mcmcBox)
        hyperParamsBoxLayout.addWidget(self._hyperparametersFrame)
        hyperParamsBox.setLayout(hyperParamsBoxLayout)
        return hyperParamsBox

    def _createRejectionBox(self):
        """Returns the ready rejection box."""

        # Create rejection settings pane
        rejectionBox = QWidget()
        rejectionBoxLayout = QGridLayout()

        # Use this for rejection
        labels = [('Number of simulations:', 'simulations'),
                  ('Threshold:', 'threshold'),
                  ('Keep:', 'keep')]

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

    def _createMCMCBox(self):
        """Returns the ready MCMC box."""

        # Create mcmc settings pane
        mcmcBox = QWidget()
        mcmcBoxLayout = QGridLayout()

        # Use this for mcmc
        firstColumn = [('Number of chains:', ASettingEntry(self._internalModel, "chains")),
                       ('Threshold:', ASettingEntry(self._internalModel, "threshold")),
                       ('Keep:', ASettingEntry(self._internalModel, "thinning"))]

        secondColumn = [("Proposal:", QComboBox()),
                        ("Optimizer:", QComboBox()),
                        ("Burn-in:", ASettingEntry(self._internalModel, "Burn"))]

        # Fill layout
        for idx in range(len(firstColumn)):
            # Add first label and selector
            mcmcBoxLayout.addWidget(QLabel(firstColumn[idx][0]), idx, 0, 1, 1)
            mcmcBoxLayout.addWidget(firstColumn[idx][1], idx, 1, 1, 1)
            # Add second label and selector
            mcmcBoxLayout.addWidget(QLabel(secondColumn[idx][0]), idx, 2, 1, 1)
            mcmcBoxLayout.addWidget(secondColumn[idx][1], idx, 3, 1, 1)

        # Set layout and return ready box
        mcmcBox.setLayout(mcmcBoxLayout)
        return mcmcBox

    def _modelTestSettingsGroup(self):
        """Create and return the model test settings groupbox."""

        # Create group boxes
        groupBox = QGroupBox('Model Test Settings')
        groupBoxLayout = QVBoxLayout()

        # Create a combo in its own widget
        self._combo = AModelComboBox(self._internalModel)
        self._combo.installEventFilter(self)

        # Create a config button
        configButton = createButton('Fix Parameters', './icons/config.png', None,
                                    self._onFixParameter, Qt.NoFocus, True)

        # Add widgets to composite widget layout
        comboWidgetLayout = QHBoxLayout()
        comboWidgetLayout.addWidget(QLabel('Pick a model:'))
        comboWidgetLayout.addWidget(self._combo)
        comboWidgetLayout.addWidget(configButton)
        comboWidgetLayout.setContentsMargins(0, 0, 0, 0)
        comboWidgetLayout.setStretchFactor(self._combo, 5)  # use for stretch
        self._comboWidget.setLayout(comboWidgetLayout)
        self._comboWidget.setEnabled(False)

        # Create a checkbox for model test
        self._modelTest = QCheckBox()
        self._modelTest.clicked.connect(self._onModelTest)
        self._modelTest.setText('Model Test')

        # Use not False, since model test is an index otherwise
        if self._internalModel.modelTest() is not False:
            self._modelTest.click()

        # Set layout of group box and return it
        groupBoxLayout.addWidget(self._modelTest)
        groupBoxLayout.addWidget(self._comboWidget)
        groupBox.setLayout(groupBoxLayout)
        return groupBox

    def eventFilter(self, qobject, event):
        """
        Adds an event poll function to the frame, 
        update combobox when mouse pressed.
        """

        if type(qobject) is AModelComboBox:
            if event.type() == QEvent.MouseButtonPress:
                self._combo.updateItems()
        return False

    def _onObjective(self, button):
        """Triggered when objective radio button clicked."""

        if button.text() == "Model Comparison":
            self._methodButtons["buttons"]["mcmc"].setEnabled(False)
        else:
            self._methodButtons["buttons"]["mcmc"].setEnabled(True)

    def _onMethod(self, button):
        """Triggered when method radio button clicked."""

        if button.text() in ["Rejection", "Random Forest"]:
            # Change view to rejection settings
            self._hyperparametersFrame.setCurrentIndex(0)
        else:
            # Change view to mcmc settings
            self._hyperparametersFrame.setCurrentIndex(1)

    def _onModelTest(self, checked):
        """Controls the appearance of the model test frame."""

        if checked:
            # Enable selector pane
            self._comboWidget.setEnabled(True)
            # Update list with models
            self._combo.updateItems()
            # Add current first model to model test
            self._internalModel.addModelIndexForTest(self._combo.currentIndex())
        else:
            self._comboWidget.setEnabled(False)
            self._internalModel.addModelIndexForTest(False)

    def _onAutoThreshold(self, checked):
        """Activated when user checks/unchecks auto threshold."""

        if checked:
            self._internalModel.changeSetting('threshold', -1)
            self._settingEntries['threshold'].setEnabled(False)
        else:
            self._settingEntries['threshold'].setEnabled(True)
            self._internalModel.changeSetting('threshold', self._settingEntries['threshold'].value())

    def _onFixParameter(self):
        """Invoke a dialog for settings parameters."""

        # Do some error checks
        if not self._internalModel.models():
            msg = QMessageBox()
            text = 'Project should contain at least one model.'
            msg.critical(self, 'Error loading data file...', text)
        else:
            dialog = AFixParameterDialog(self._internalModel, self.nativeParentWidget())
            dialog.exec_()


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

        # Particles settings
        if self._key == 'simulations':
            self.setRange(0, 1e10)
            self.setSingleStep(10)
            self.setDecimals(0)

    def _onValueChanged(self, val):
        """Triggered when user changes the value fo the setting."""
        pass
        #self._internalModel.changeSetting(self._key, val)


class AOuputDir(QWidget):
    """Main output dir widget for specifying output location."""
    def __init__(self, internalModel, parent=None):
        super(AOuputDir, self).__init__(parent)

        self._internalModel = internalModel
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Creates and sets the layout."""

        # Create edit for path
        self._path = QLineEdit()
        self._path.setPlaceholderText('Output location...')
        self._path.setText(self._internalModel.outputDir())
        self._path.textChanged.connect(self._onEdit)

        # Create button for dir
        self._button = createButton("", './icons/load.png', 'Select output directory...',
                                    self._onOpen, Qt.NoFocus, True, True)

        # Add widgets to layout
        layout.addWidget(self._button)
        layout.addWidget(self._path)
        layout.setSpacing(0)

        self.setLayout(layout)

    def _onOpen(self):
        """Opens up a file dialog for choosing an output folder."""

        # Create file dialog
        dirPath = QFileDialog.getExistingDirectory(self, 'Select an Empty Output Directory...',
                                                   '', QFileDialog.ShowDirsOnly)

        # If user has selected something
        if dirPath:
            # Update entry
            self._path.setText(dirPath)
            self._internalModel.addOutputDir(dirPath)
            # Modify save flag
            tracksave.saved = False

    def _onEdit(self, text):
        """Triggered when user types into dir edit."""

        self._internalModel.addOutputDir(text)


class ARunFrame(QScrollArea):
    """Main container for the model testing"""
    def __init__(self, internalModel, console, outputConsole, parent=None):
        super(ARunFrame, self).__init__(parent)

        self._internalModel = internalModel
        self._console = console
        self._outputConsole = outputConsole
        self._processManager = AProcessManager(self, self._internalModel,
                                               self._console,
                                               self._outputConsole)
        self._configureLayout(QVBoxLayout())

    def _configureLayout(self, layout):
        """Lays out main components of the frame."""

        self.setFrameStyle(QFrame.Panel)

        runGroupBox = QGroupBox('Computation')
        runGroupBoxLayout = QHBoxLayout()

        # Create run abd stop buttons
        self._run = createButton('Run', './icons/run', "Run ABC estimation...",
                                       self._onRun, Qt.NoFocus, True)
        self._stop = createButton('Stop', './icons/stop', "Abort ABC.",
                                        self._onStop, Qt.NoFocus, False)
        # Create progress bar
        self._progress = QProgressBar()
        self._progress.setOrientation(Qt.Horizontal)

        # Add buttons and progress bar to runbox layout
        runGroupBoxLayout.addWidget(self._run)
        runGroupBoxLayout.addWidget(self._stop)
        runGroupBoxLayout.addStretch(0)
        runGroupBoxLayout.addWidget(self._progress)
        runGroupBoxLayout.setStretchFactor(self._progress, 3)
        runGroupBox.setLayout(runGroupBoxLayout)

        layout.addWidget(runGroupBox)
        layout.addStretch(1)

        # Inner widget of scrollarea
        content = QWidget()
        content.setLayout(layout)

        # Place inner widget inside the scrollable area
        self.setWidget(content)
        self.setWidgetResizable(True)

    def _onRun(self):
        """For debugging."""

        if self._internalModel.sanityCheckPassed(self.nativeParentWidget()):

            # Create an executable python script in the output dir
            scriptCreator = AScriptCreator(self._internalModel)
            scriptName = scriptCreator.createScript()

            # Start a python process in e separate thread
            self._processManager.startAbc(scriptName)

    def _onStop(self):
        """Kill python thread and subprocess inside."""

        self._processManager.stopAll()

    def signalAbcStarted(self):
        """Signaled from the process manager."""

        # Start progress bar
        self._progress.setMinimum(0)
        self._progress.setMaximum(0)
        self._progress.show()

        # Disable run button, enable stop
        self._run.setEnabled(False)
        self._stop.setEnabled(True)

    def signalAbcFinished(self, error):
        """Signaled from the process manager."""

        # Disable stop button, enable run
        self._run.setEnabled(True)
        self._stop.setEnabled(False)

        # Hide progress
        self._progress.hide()

        # Load pickled var, if no error thrown from process
        if not error:
            self._loadPickledResults()

    def signalAbcAborted(self):
        """Signaled from the process manager."""

        # Disable stop button, enable run
        self._run.setEnabled(True)
        self._stop.setEnabled(False)

        # Hide progress
        self._progress.hide()

    def _loadPickledResults(self):
        """Called when algorithm finished."""

        # Get dict name
        name = self._internalModel.outputDir() + '/' + 'save.p'

        # Unpickle
        unpickled = pickle.load(open(name, 'rb'))

        # Push to console and write to output console
        self._console.addResults(unpickled)
        self._outputConsole.write('You can access your results by typing '
                                  '<strong>results</strong> in the Python console.')


class AModelComboBox(QComboBox):
    """Represent a dynamically changing combobox."""
    def __init__(self, internalModel, parent=None):
        super(AModelComboBox, self).__init__(parent)

        self._internalModel = internalModel
        self.currentIndexChanged.connect(self._onIndexChange)

    def _onIndexChange(self, idx):
        """Update internal model with model index."""
        if idx >= 0:
            self._internalModel.addModelIndexForTest(idx)

    def updateItems(self):
        """Clear items and add new (need to do dynamically.)"""
        self.clear()
        for idx, model in enumerate(self._internalModel['models']):
            self.addItem(model.name)
            self.setItemIcon(idx, QIcon('./icons/model.png'))


class ACheckBox(QCheckBox):
    def __init__(self, value, parent=None):
        super(ACheckBox, self).__init__(parent)

        self.value = value
        self.setText(value.capitalize())
