from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QAbstractTableModel
from abrox.gui.a_dialogs import ALoadDataDialog
from abrox.gui.a_utils import createButton
from abrox.gui import tracksave
import pandas as pd


class ADataViewer(QFrame):
    """Represents a container for the table showing loaded data files."""

    def __init__(self, model, console, outputConsole, parent=None):
        super(ADataViewer, self).__init__(parent)

        # Add references to attributes
        self._internalModel = model
        self._table = APandasView(console, outputConsole, self._internalModel)
        self._toolbar = ATableToolbar(model, self._table, console)
        self._configureLayout(QVBoxLayout())

        # Update table, if any data
        if self._internalModel.dataFile() is not None:
            self._table.updateTableAndModel()
            self._toolbar.updateLoadedFileLabel()

    def _configureLayout(self, layout):
        """Lays out the main components."""

        self.setFrameStyle(QFrame.Panel)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._table)
        self.setLayout(layout)


class APandasView(QTableView):
    """Represents the table view for the pandas data model."""

    def __init__(self, console, outputConsole, internalModel, parent=None):
        super(APandasView, self).__init__(parent)

        self._console = console
        self._outputConsole = outputConsole
        self._internalModel = internalModel

    def updateTableAndModel(self):
        """A proxy method to update table."""

        # Get data frame and file name
        data, dataFileName = self._loadDataWithPandas()

        #  Make sure something is returned
        if data is not None:
            # Create model
            model = APandasModel(data)

            # Add model to table
            self.setModel(model)

            # Push DataFrame to IPython
            self._console.addData(data)

            # Write hint to output console
            self._outputConsole.write('\n')
            self._outputConsole.write('File {} successfully loaded.'.format(dataFileName))
            self._outputConsole.write('You can access your data by typing <strong>data</strong> '
                                      'in the Python console.\n')

    def clearTableAndModel(self):
        """Takes care of clearing data and any references to it."""

        # Clear from model
        self._internalModel.clearData()
        # Set an empty model
        self.setModel(APandasModel(pd.DataFrame()))
        # Remove form console
        self._console.removeData()

    def _loadDataWithPandas(self):
        """
        Attempts ot load data as defined in the model.
        Returns the loaded pandas DataFrame and the data
        file name as provided by the internal model.
        """

        dataFileName, delim = self._internalModel.dataFileAndDelimiter()
        try:
            data = pd.read_csv(dataFileName, delimiter=delim, header=0)
            return data, dataFileName
        except IOError as e:
            QMessageBox.critical(self, 'Could not load file {}'.format(dataFileName),
                                 str(e), QMessageBox.Ok)
            return None, None


class APandasModel(QAbstractTableModel):
    """
    Class to populate a Qt table view with a pandas data frame.
    Credit goes to: https://github.com/SanPen/GridCal/blob/master/UnderDevelopment/GridCal/gui/GuiFunctions.py
    """
    def __init__(self, data, parent=None, editable=False, editable_min_idx=-1):
        super(APandasModel, self).__init__(parent)
        self.data = data
        self._cols = data.columns
        self.index = data.index.values
        self.editable = editable
        self.editable_min_idx = editable_min_idx
        self.r, self.c = self.data.shape
        self.isDate = False
        self.formatter = lambda x: "%.2f" % x

    def flags(self, index):
        if self.editable and index.column() > self.editable_min_idx:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.DisplayRole):

        try:
            self.data.iloc[index.row(), index.column()] = value
        except TypeError:
            QMessageBox.critical(self, 'Error...',
                                 'Trying to fill in data with a different format',
                                 QMessageBox.Ok)

    def headerData(self, p_int, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == Qt.Vertical:
                if self.index is None:
                    return p_int
                else:
                    if self.isDate:
                        return self.index[p_int].strftime('%Y/%m/%d  %H:%M.%S')
                    else:
                        return str(self.index[p_int])
        return None

    def copy_to_column(self, row, col):
        """
        Copies one value to all the column
        @param row: Row of the value
        @param col: Column of the value
        @return: Nothing
        """
        self.data.iloc[:, col] = self.data.iloc[row, col]


class ATableToolbar(QFrame):
    """Represents a toolbar for the table."""

    def __init__(self, model, table, parent=None):
        super(ATableToolbar, self).__init__(parent)

        self._internalModel = model
        self._table = table
        self._label = QLabel('No Data File Loaded...  ')
        self._configureLayout(QHBoxLayout())

    def updateLoadedFileLabel(self):
        """Updates the label above the table. Assumes data file loaded."""

        self._label.setText('Showing: ' + self._internalModel.dataFile() + '  ')

    def _configureLayout(self, layout):
        """Lays out the main toolbar components"""

        self.setFrameStyle(QFrame.WinPanel)
        # adjust layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create load data button
        _loadDataButton = createButton('Load Data', 'icons/load.png', 'Load data from file...',
                                      self._onLoad,Qt.NoFocus, True)

        # Create clear data button
        self._clearDataButton = createButton('Clear Data', 'icons/clear.png', 'Clear data...',
                                      self._onClear, Qt.NoFocus, False)

        layout.addWidget(_loadDataButton)
        layout.addWidget(self._clearDataButton)
        layout.addStretch(1)
        layout.addWidget(QLabel())
        layout.addWidget(self._label)
        self.setLayout(layout)

    def _onLoad(self):
        """Activated when button clicked."""

        loadedFileName = QFileDialog.getOpenFileName(self, 'Select a data file to load...',
                                                     "", "Data Files (*.csv *.txt *.dat)")
        # If something loaded, open properties dialog
        if loadedFileName[0]:
            dialog = ALoadDataDialog(loadedFileName[0], self._internalModel, self)
            dialog.exec_()
            # If dialog accepted and loading ok
            if dialog.accepted:
                # Update table and table model
                self._table.updateTableAndModel()
                # Update toolbar text
                self.updateLoadedFileLabel()
                # Update save flag
                tracksave.saved = False
                # Enable clear
                self._clearDataButton.setEnabled(True)

    def _onClear(self):
        """Removes reference to data file, clears table and model."""

        # Delegate clearing to data viewer
        self._table.clearTableAndModel()
        # Disable button since no datacls

        self._clearDataButton.setEnabled(False)

