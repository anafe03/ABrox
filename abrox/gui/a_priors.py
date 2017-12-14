from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import stats
import matplotlib as mpl
import numpy as np
from collections import OrderedDict
from abrox.gui import tracksave


class APriorsWindow(QScrollArea):
    """
    This class represents the frame for the APriorSpecifier
    (left) and APriorPlot (right).
    """
    def __init__(self, internalModel, model, parent=None):
        super(APriorsWindow, self).__init__(parent)

        self._plotter = APriorPlot()
        self._specifier = APriorSpecifier(internalModel, model, self._plotter)
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Places the specifier and the plotter into hlayout."""

        self.setFrameShape(QFrame.Panel)

        splitter = QSplitter()
        splitter.addWidget(self._specifier)
        splitter.addWidget(self._plotter)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        layout.addWidget(splitter)

        # Inner widget of scrollarea
        content = QWidget()
        content.setLayout(layout)

        # Place inner widget inside the scrollable area
        self.setWidget(content)
        self.setWidgetResizable(True)

    def changeModelName(self, newName):
        """Called externally to change model name."""

        self._specifier.changeModelName(newName)


class APriorSpecifier(QFrame):
    """A class to represent the prior specifier widget."""

    PriorDists = OrderedDict([
        ('Normal', {
                    'params': OrderedDict([('loc', 0), ('scale', 1)]),
                    'func': 'stats.norm'
                   }),
        ('Uniform', {
                    'params': OrderedDict([('loc', 0), ('scale', 1)]),
                    'func': 'stats.uniform'
                    }),
        ('Cauchy', {
                    'params': OrderedDict([('loc', 0), ('scale', 1)]),
                    'func': 'stats.cauchy'
                   }),
        ('Exponential', {
                    'params': OrderedDict([('loc', 0), ('scale', 1)]),
                    'func': 'stats.expon'
                    }),
        ('Binomial', {
                    'params': OrderedDict([('n', -1), ('p', -1), ('loc', 0)]),
                    'func': 'stats.binom'
                    }),
        ('Poisson', {
                    'params': OrderedDict([('mu', -1), ('loc', 0)]),
                    'func': 'stats.poisson'
                    }),
        ('Beta',    {
                    'params': OrderedDict([('a', -1), ('b', -1), ('loc', 0)]),
                    'func': 'stats.beta'
                    }),
        ('Gamma', {
                    'params': OrderedDict([('a', -1), ('loc', 0), ('scale', 1)]),
                    'func': 'stats.gamma'
                    }),
        ('Inverse Gamma', {
                    'params': OrderedDict([('a', -1), ('loc', 0), ('scale', 1)]),
                    'func': 'stats.invgamma'
                    }),
        ('Geometric', {
                    'params': OrderedDict([('p', -1), ('loc', 0)]),
                    'func': 'stats.geom'
                    })
        ])

    def __init__(self, internalModel, model, plotter, parent=None):
        super(APriorSpecifier, self).__init__(parent)

        self._plotter = plotter
        self._priorList = APriorList(internalModel, model, self._plotter)
        self._priorSelector = APriorSelector(internalModel, model, self._priorList)
        self._initSpecifier(QVBoxLayout())

    def _initSpecifier(self, layout):
        """Lays out the main components of the specifier."""

        self.setFrameShape(QFrame.Panel)
        layout.addWidget(self._priorSelector)
        layout.addWidget(self._priorList)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def changeModelName(self, newName):
        """Called externally to change the model name."""

        self._priorList.modelName = newName
        self._priorSelector.modelName = newName

    def onLoadProject(self, model):
        """Called when a project is loaded as a proxy to the list's project."""

        self._priorList.onLoadProject(model)


class APriorPlot(QFrame):
    """This class represents a plot pane for plotting prior dists."""

    def __init__(self, parent=None):
        super(APriorPlot, self).__init__(parent)

        # Create the figure object
        self.figure = Figure(facecolor='#31363b')
        # Create the canvas widget as container
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(self.canvas.size())
        FigureCanvas.updateGeometry(self)
        self._configureStyle()
        self.figure.gca().xaxis.grid(True)
        self._configurePlotter(QVBoxLayout())

    def _configureStyle(self):
        """Determines the colors of the plot."""

        mpl.rcParams['axes.labelcolor'] = '#eff0f1'
        mpl.rcParams['text.color'] = '#eff0f1'
        mpl.rcParams['axes.facecolor'] = '#232629'
        mpl.rcParams['xtick.color'] = '#eff0f1'
        mpl.rcParams['ytick.color'] = '#eff0f1'
        mpl.rcParams['axes.linewidth'] = 0.5
        mpl.rcParams['grid.alpha'] = 0.5
        mpl.rcParams['axes.grid'] = True

    def _configurePlotter(self, layout):
        """Lays out the plotter frame."""

        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setFrameShape(QFrame.Panel)

    def clearPlot(self):
        """Called to clear canvas from current plot."""

        self.figure.clear()
        self.canvas.draw()

    def plotExample(self, funcCode):
        """Called to plot an example distribution via scipy function."""

        # Clear figure
        self.figure.clear()

        # Create some example values
        X = np.arange(-5, 5, 0.1)

        #self.figure.tight_layout()
        ax = self.figure.add_subplot(1, 1, 1)
        # Create a scipy object and get pdf
        sciDist = eval(funcCode)

        # Plot example function
        try:
            y = sciDist.pdf(X)
            self._plotContinuous(ax, X, y)
        except AttributeError:
            y = sciDist.cdf(X)
            self._plotDiscrete(ax, X, y)

        self.canvas.draw()

    def _plotContinuous(self, ax, X, y):
        """Plot a continuous random variable."""

        ax.set_title('Probability Density Function')
        ax.plot(X, y, linewidth=2)
        ax.set_xlabel('X')
        ax.set_ylabel('y')

    def _plotDiscrete(self, ax, X, y):
        """Plot a continuous random variable."""

        ax.set_title('Cumulative Density Function')
        ax.plot(X, y, linewidth=2)
        ax.set_xlabel('X')
        ax.set_ylabel('y')


class APriorCombo(QComboBox):
    """This class represents a drop-down for selecting parameters."""

    def __init__(self, options, parent=None):
        super(APriorCombo, self).__init__(parent)

        self.addItems(options)


class APriorList(QListWidget):
    """This class represents a list for displaying parameters."""

    def __init__(self, internalModel, model, plotter, parent=None):
        super(APriorList, self).__init__(parent)

        # Set reference to internal model and plotter
        self._internalModel = internalModel
        self.modelName = model.name
        self._plotter = plotter

        # Configure list properties
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._onContext)
        self.clicked.connect(self._onItemClick)
        self.itemEntered.connect(self._onItemEnter)

        # Fill list, or add dummy if empty
        self._dummy = False
        self._populate(model)

    def _populate(self, model):
        """Called either after add model or after project load."""

        if model.hasPriors():
            # Model has priors, add them
            # Iterate over priors
            for prior in model:
                # Each prior is a single name - func dict, so we iterate once
                for key, val in prior.items():
                    self.addPrior(APriorListItem(key, val, 9))
        else:
            # Model has no priors, simply add dummy
            self._dummy = True
            self.addItem(ADummyItem('No priors defined...'))

    def addPrior(self, item):
        """Interface to add prior item to list."""

        if self._dummy:
            # Remove dummy
            self.takeItem(0)
            self._dummy = False
        # Add prior to list
        self.addItem(item)
        tracksave.saved = False

    def _deleteItems(self):
        """Removes files from list and model."""

        # Get selected items
        items = self.selectedItems()

        # Remove items from list
        for i, item in enumerate(items):
            idx = self.indexFromItem(item)
            self.takeItem(idx.row())
            self._internalModel.deletePriorFromModel(idx.row(), self.modelName)

        # Check if any items left
        if self.count() == 0:
            self.addItem(ADummyItem('No priors defined...'))
            self._plotter.clearPlot()
            self._dummy = True

        tracksave.saved = False

    def _onContext(self, point):
        """Activated on right-click from user."""

        if not self._dummy:
            menu = QMenu()
            deleteAction = QAction("Remove Prior(s)")
            deleteAction.triggered.connect(self._deleteItems)
            menu.addAction(deleteAction)
            menu.exec_(self.mapToGlobal(point))

    def _onItemClick(self, itemIdx):
        """Triggered when item clicked."""

        if not self._dummy:
            # Get distribution generating function code
            code = self.itemFromIndex(itemIdx).funcCode
            self._plotter.plotExample(code)

    def keyPressEvent(self, event):
        """Checks for delete key and removes currently selected if pressed."""

        key = event.key()

        if key == Qt.Key_Delete:
            if not self._dummy:
                self._deleteItems()
                # Modify save flag
                tracksave.saved = False

        QListWidget.keyPressEvent(self, event)

    def _onItemEnter(self, item):

        if not self._dummy:
            self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, leave):

        self.setCursor(Qt.ArrowCursor)


class APriorSpinBox(QDoubleSpinBox):
    """Represents a modified spinbox for a parameter value."""
    def __init__(self, valRange, parent=None):
        super(APriorSpinBox, self).__init__(parent)

        self.setRange(valRange[0], valRange[1])


class APriorListItem(QListWidgetItem):
    """Represents a modified list widget for a parameter value."""
    def __init__(self, parName, funcCode, fontSize, parent=None):
        super(APriorListItem, self).__init__(parent)

        self.parName = parName
        self.funcCode = funcCode
        font = QFont(self.font())
        font.setPointSize(fontSize)
        self.setFont(font)
        self.setText('Prior ' + parName + ': ' + '~' + funcCode)
        self.setIcon(QIcon('./icons/prior.png'))


class ADummyItem(QListWidgetItem):
    """A class to represent a dummy list widget item with some text."""

    def __init__(self, text, parent=None):
        super(ADummyItem, self).__init__(parent)

        font = self.font()
        font.setPointSize(9)
        self.setFont(font)
        self.setText(text)


class APriorSelector(QWidget):
    """This class is a container for all parameter definition choices."""
    def __init__(self, internalModel, model, priorList, parent=None):
        super(APriorSelector, self).__init__(parent)

        self._internalModel = internalModel
        self.modelName = model.name
        self._priorList = priorList
        self._initPriorSelector(QGridLayout())

    def _initPriorSelector(self, layout):
        """Lays out the main components of the selector"""

        # Create widgets
        self._combo = APriorCombo(APriorSpecifier.PriorDists.keys())
        self._combo.currentTextChanged[str].connect(self._onDistChange)

        self._name = QLineEdit()
        self._name.setPlaceholderText('Parameter name')

        standardRange = (-10e10, 10e10)
        self._entries = [APriorSpinBox(standardRange),
                         APriorSpinBox(standardRange),
                         APriorSpinBox(standardRange)]
        # Disable last, since default normal dist has only two params
        self._entries[1].setValue(1.0)
        self._entries[2].setDisabled(True)
        self._define = QPushButton('Define')
        self._define.setIcon(QIcon('./icons/define.png'))
        self._define.clicked.connect(self._onDefine)
        # Define labels
        self._labels = [QLabel('Parameter Name', self),
                        QLabel('Prior Distribution', self),
                        QLabel('Dist. Param: <b>loc</b>', self),
                        QLabel('Dist. Param: <b>scale</b>', self),
                        QLabel('', self)]

        # Add labels to layout
        for idx, label in enumerate(self._labels):
            layout.addWidget(label, 0, idx)

        # Add widgets to layout
        for idx, widget in enumerate([self._name] +
                                     [self._combo] +
                                      self._entries +
                                      [self._define]):
            layout.addWidget(widget, 1, idx)

        self.setLayout(layout)

    def _onDistChange(self, distName):
        """Activated when distribution selection changes."""

        # Get current distribution dict
        current = APriorSpecifier.PriorDists[distName]

        # Loop through parameters and change labels
        for idx, key in enumerate(current['params'].keys()):
            self._entries[idx].setEnabled(True)
            self._entries[idx].setValue(current['params'][key])
            self._labels[idx+2].setText('Dist. Param: <b>' + key + '</b>')

        # Check for distributions with 2 parameters
        if len(current['params'].keys()) < 3:
            self._labels[4].setText('')
            self._entries[2].setDisabled(True)

    def _onDefine(self):
        """Activated when user pressed define parameter button."""

        # Unfocus button
        self.setFocus(False)

        # Get current generating code
        code = self._getSciPyCode()

        # Check for no name entered
        if self._name.text() == "":
            QToolTip.showText(self.mapToGlobal(self._name.rect().bottomLeft()),
                              'Parameter must have a name.',
                              None)
        else:
            # Try to add to model prior list
            if self._internalModel.addPriorToModel(self._name.text(), code, self.modelName):
                # Add to listbox and remove old name
                self._priorList.addPrior(APriorListItem(self._name.text(), code, fontSize=9))
                self._name.setText("")
            else:
                QToolTip.showText(self.mapToGlobal(self._name.rect().bottomLeft()),
                                  'Parameter name taken.',
                                  None)

    def _getSciPyCode(self):
        """Returns the SciPy distribution code for the selected prior."""

        # Get current dist name
        current = self._combo.currentText()
        currentDist = APriorSpecifier.PriorDists[current]

        # Get current generating code
        currentCode = currentDist['func'] + '('
        for idx, key in enumerate(currentDist['params'].keys()):
            currentCode += key + '=' + str(self._entries[idx].value()) + ', '
        currentCode += ')'
        currentCode = currentCode.replace(', )', ')')
        return currentCode



