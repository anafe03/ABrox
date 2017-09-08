import numpy as np
import matplotlib.pyplot as plt


plt.style.use('dark_background')

fig, ax = plt.subplots()

L = 6
x = np.linspace(0, L)
ncolors = len(plt.rcParams['axes.prop_cycle'])
shift = np.linspace(0, L, ncolors, endpoint=False)
for s in shift:
    ax.plot(x, np.sin(x + s), 'o-')
ax.set_xlabel('x-axis')
ax.set_ylabel('y-axis')
ax.set_title("'dark_background' style sheet")

plt.show()


class ATable(QTableWidget):
    """Represents a table to display loaded data files."""

    def __init__(self, model, parent=None):
        super(ATable, self).__init__(parent)

        self._internalModel = model
        self._initTable()

    def _initTable(self):
        """Initializes and configures the table."""

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def updateTable(self, data):
        """Updates the table view."""

        # get row and column counts
        r = data.shape[0]
        c = data.shape[1]
        print('Calculated shape:', r, c)
        print('Column names: ', data.columns.values.tolist())
        # call populate helper
        self._populate(data, r, c)

    def clearTable(self):
        """Clears all entries."""

        while self.rowCount() > 0:
            self.removeRow(0)
        self.horizontalHeader().hide()

    def _populate(self, data, r, c):
        """
        Accept a pandas DataFrame.
        Populates table according to num columns and rows.
        """

        self.setRowCount(r)
        self.setColumnCount(c)
        #self.setHorizontalHeaderLabels(data.columns.values.tolist())

        # use for performance
        self.blockSignals(True)


        for i in range(r):
            for j in range(c):
                item = QTableWidgetItem()
                item.setText(str(data[i, j]))
                self.setItem(i, j, item)
        self.horizontalHeader().show()
        self.blockSignals(False)