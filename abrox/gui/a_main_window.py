from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
from collections import OrderedDict
import tracksave
import time
from a_tree import AModelTree
from a_pyconsole import AConsoleWindow
from a_console import AOutputConsole
from a_model import AInternalModel
from a_utils import *


class AMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(AMainWindow, self).__init__(parent)

        self._internalModel = AInternalModel()
        self._mdiArea = QMdiArea()
        self._console = AConsoleWindow()
        self._outputConsole = AOutputConsole(self._internalModel)
        self._initMain()

    def _initMain(self):
        """Initialize relevant parts of main window."""

        self._configureWindow()
        self._configureMenu()
        self._configureToolbar()
        self._configureMain()
        self._configureConsole()
        self._configureTree()

    def _configureWindow(self):
        """Applies main settings to main window."""

        self.statusBar()
        self.setWindowIcon(QIcon('./icons/icon.ico'))
        self.setWindowTitle('ABrox - A tool for Approximate Bayesian Computation')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setDockOptions(QMainWindow.AnimatedDocks |
                            QMainWindow.AllowNestedDocks |
                            QMainWindow.AllowTabbedDocks)

    def _configureMenu(self):
        """Configure menu bar."""

        # Create top-level menus
        fileMenu = self.menuBar().addMenu('&File')
        toolsMenu = self.menuBar().addMenu('&Tools')
        viewMenu = self.menuBar().addMenu('&View')
        helpMenu = self.menuBar().addMenu('&Help')

        # Create submenu for toggling panes
        self._paneViewMenu = viewMenu.addMenu('Toggle Panes')

        # Create submenu for changing display of MDI area
        _mdiView = viewMenu.addMenu('Workspace View')
        group = QActionGroup(self)
        group.setExclusive(True)
        tabbedAction = createAction('Tabbed View', callback=self._tabbed, parent=_mdiView,
                                    tip='Organize workfiles as separate tabs', checkable=True)
        stackedAction = createAction('Stacked View', callback=self._stacked, parent=_mdiView,
                                     tip='Organize workfiles as floating windows', checkable=True)

        tabbedAction.setChecked(True)
        group.addAction(stackedAction)
        group.addAction(tabbedAction)
        addActionsToMenu(_mdiView, (stackedAction, tabbedAction))

        fontAction = createAction('Editor Font...', callback=self._openFontDialog, parent=self,
                                  tip='Configure editor font', checkable=False)
        addActionsToMenu(viewMenu, (fontAction, ))

        # Create actions for file menu
        loadData = createAction('&Load Data...', callback=self._loadData, parent=fileMenu,
                                tip="Load data file(s)...", icon='open')
        loadSession = createAction('&Load Project...', callback=self._loadSession, parent=fileMenu,
                                   tip='Load project...', icon='loadsession')
        saveSession = createAction('&Save Project', callback=self._saveSession, parent=fileMenu,
                                   tip='Save current project...', icon='save')
        exitAction = createAction('&Exit', callback=self.close, tip='Quit ABrox', parent=fileMenu,)

        # Add actions to file menu
        addActionsToMenu(fileMenu, (loadData, loadSession, saveSession, None, exitAction))

        # Add actions to view menu

    def _configureToolbar(self):
        """Sets up toolbar for helper methods."""

        # Create toolbar
        toolbar = self.addToolBar('Toolbar')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        loadSession = createAction('&Load Project', callback=self._loadSession, parent=self,
                                   tip='Load project...', icon='loadsession')
        saveSession = createAction('&Save Project', callback=self._saveSession, parent=self,
                                   tip='Save current project...', icon='savesession')
        # Add actions to toolbar
        addActionsToMenu(toolbar, (loadSession, saveSession))

    def _configureMain(self):
        """Set up the workspace for editing code."""

        self._mdiArea.setViewMode(QMdiArea.TabbedView)
        self._mdiArea.setTabsClosable(True)
        self._mdiArea.setTabsMovable(True)
        self._mdiArea.setBackground(QColor(35, 38, 41))
        self._mdiArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self._mdiArea)

    def _configureConsole(self):
        """Set up the python console and the output console."""

        # Create the console dock widget
        consoleDockWidget = QDockWidget("Console Window", self)
        consoleDockWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        consoleDockWidget.setObjectName("PyConsoleDockWidget")
        consoleDockWidget.setAllowedAreas(Qt.AllDockWidgetAreas)
        consoleDockWidget.setFeatures(QDockWidget.AllDockWidgetFeatures)

        # Add console to dock and toggle view action to menu
        self._paneViewMenu.addAction(consoleDockWidget.toggleViewAction())

        # Create a tab controller
        self.outputConsole = QLabel('WTF')
        settings = [(self._console, "Python Console", 0, "./icons/py.png"),
                    (self._outputConsole, "Output Console", 1, "./icons/output.png")]
        self._tabController = ATabController(settings)

        consoleDockWidget.setWidget(self._tabController)
        self.addDockWidget(Qt.BottomDockWidgetArea, consoleDockWidget)

    def _configureTree(self):
        """Set up the tree for modifying the session structure."""

        # Create the tree widget
        self._tree = AModelTree(self._mdiArea, self._internalModel,
                                self._console, self._outputConsole)

        # Create the dock widget
        treeDockWidget = QDockWidget("Project Tree", self)
        treeDockWidget.setObjectName("ExpTreeDockWidget")
        treeDockWidget.setAllowedAreas(Qt.AllDockWidgetAreas)
        treeDockWidget.setFeatures(QDockWidget.AllDockWidgetFeatures)

        # Add console to dock
        treeDockWidget.setWidget(self._tree)

        # Add dock toggle to view menu
        self._paneViewMenu.addAction(treeDockWidget.toggleViewAction())

        # Add dock to main
        self.addDockWidget(Qt.LeftDockWidgetArea, treeDockWidget)

    def _loadData(self):
        """Load data into table."""

        pass

    def _loadSession(self):
        """Load a previously saved session."""

        # Create a dialog
        loadName = QFileDialog.getOpenFileName(self, 'Select a project file to open...',
                                                     "", "bprox File (*.bprox)")
        # Check if something loaded
        if loadName[0]:

            # Ask for save of current, if something loaded
            if not tracksave.saved:
                # Create a dialog
                dialog = QMessageBox()
                # Ask if user sure
                choice = dialog.question(self, 'Loading a new project...',
                                         'Do you want to save your current project?',
                                         QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes)
                if choice == QMessageBox.Yes:
                    self._saveSession()

            # Check header
            with open(loadName[0], 'r') as infile:
                # Check first line for header
                if '[ABrox Project File]' in infile.readline():
                    # Load with json
                    newProject = json.load(infile, object_pairs_hook=OrderedDict)
                    # Overwrite internal model
                    self._internalModel.overwrite(newProject)
                    # Update tree
                    self._tree.updateProject()
                    # Modify save flag
                    tracksave.saved = True
                else:
                    QMessageBox.critical(self, 'Error loading file',
                                         'Could not load file. The format is not supported by ABrox.',
                                         QMessageBox.Ok)

    def _saveSession(self):
        """Save the current settings."""

        saveName = QFileDialog.getSaveFileName(self, "Save current project as...",
                                                     "", "bprox File (*.bprox)")
        # If user has chosen something
        if saveName[0]:
            # Get project as dict
            projectAsDict = self._tree.toDict()
            # Open file and dump as json
            try:
                with open(saveName[0], 'w') as outfile:
                    # Write header
                    outfile.write('[ABrox Project File]\n')
                    # Write json model
                    json.dump(projectAsDict, outfile, indent=4)
            except IOError as e:
                QMessageBox.critical(self, 'Error saving file',
                                     'Could not save file due to: '.format(str(e)),
                                     QMessageBox.Ok)

            tracksave.saved = True

    def _stacked(self):
        """Activated when user clicks the stacked menu button."""
        self._mdiArea.setViewMode(QMdiArea.SubWindowView)

    def _tabbed(self):
        """Activated when user clicks the tabbed view menu button."""
        self._mdiArea.setViewMode(QMdiArea.TabbedView)

    def _openFontDialog(self):
        """Opens a font menu and changes the font of all editors on select."""

        currentFont = self._tree.currentEditorFont()
        print(currentFont.family())

        font, valid = QFontDialog.getFont(currentFont, self, 'Select Font for Editor')
        if valid:
            #font.setFixedPitch(True)
            #font = QFont('Monospaced', 12)
            font.setFixedPitch(True)
            self._tree.changeEditorFont(font)

    def closeEvent(self, event):
        """Override close event so a dialog can be displayed before closing."""

        if not tracksave.saved:
            # Create a dialog
            dialog = QMessageBox()
            # Ask if user sure
            choice = dialog.question(self, 'Exiting ABrox...',
                                     'Do you want to save your current project?',
                                     QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes)
            # Check user choice
            if choice == QMessageBox.Yes:
                self._saveSession()
                event.accept()
            elif choice == QMessageBox.No:
                event.accept()
            elif choice == QMessageBox.Cancel:
                event.ignore()
        else:
            QMainWindow.closeEvent(self, event)


class FastDmStatus(QStatusBar):

    def __init__(self, parent=None):
        super(FastDmStatus, self).__init__(parent)

        self._label = QLabel("Ready")
        self.setStyleSheet("border: 1px solid #535b68")
        self.addPermanentWidget(self._label)

    def changeStatus(self, txt):
        """Changes status to text."""

        self._label.setText(txt)


class AStartUp(QWidget):

    def __init__(self, parent=None):
        super(AStartUp, self).__init__(parent)

        layout = QHBoxLayout()
        button1 = QPushButton('Start New Session')
        button2 = QPushButton('Load Session')
        layout.addWidget(button1)
        layout.addWidget(button2)
        self.setLayout(layout)


class ATabController(QTabWidget):
    """Main representation of a tab widget. Constructor expects
    an iterable with 4-tuple items containing (widget, text, idx icon name)."""
    def __init__(self, tabSettings, parent=None):
        super(ATabController, self).__init__(parent)

        self._configureTabs(tabSettings)
        self.setTabPosition(QTabWidget.South)
        self.currentChanged.connect(self._onTabChange)

    def _configureTabs(self, settings):
        """Configures tab layout and size policy."""

        for tab in settings:
            self.addTab(tab[0], tab[1])
            self.setTabIcon(tab[2], QIcon(tab[3]))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def _onTabChange(self, idx):
        """Use to change window text of dock widget when tabs change."""

        if idx == 0:
            self.parent().setWindowTitle('Python Console')
        else:
            self.parent().setWindowTitle('Output Console')