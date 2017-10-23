import pandas as pd
import numpy as np
from abc_utils import toArray


class AbcReferenceTable:
    """
    Holds the final ABC Table where each row corresponds to one simulation.
    Contains information about:
     - model index
     - summary statistics
     - drawn parameters
     - distance to observed data
    """

    def __init__(self):
        self._table = None

    def initialize(self, content):
        """ Initialize Reference Table."""

        cols = ['idx','param','sumstat','distance']
        self._table = pd.DataFrame(content,columns=cols)

    def getTable(self):
        """ Return Reference Table."""
        return self._table

    def fillColumn(self, data, columnName):
        """
        Store data in ABC Table column.
        Used to store summary statistics back into ABC Table
        after scaling.
        """
        if columnName == 'sumstat':
            data = [np.array(row) for row in data]
        self._table[columnName] = data

    def getColumn(self, columnName):
        """ Get column as numpy array"""
        return toArray(self._table,columnName)

    def fillRow(self, row, idx, param, sumstat):
        """Fill a row of the table. Distance is calculated later."""

        self._table.loc[row, 'idx'] = idx
        self._table.set_value(row, 'param', param)
        self._table.set_value(row, 'sumstat', sumstat)

