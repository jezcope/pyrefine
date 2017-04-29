"""Operations that operate on whole columns.

.. autosummary::

    ColumnRemovalOperation
    ColumnRenameOperation
    ColumnMoveOperation
"""
from .base import operation


@operation('column-removal')
class ColumnRemovalOperation:
    """Remove a specified column from the dataset.

    Expects a ``dict`` as loaded from OpenRefine JSON script.

    Args:
        parameters['description'] (str): Human-readable description
        parameters['columnName'] (str): Column to remove
    """

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.column = parameters['columnName']

    def execute(self, data):
        """Remove the specified column from ``data``.

        The column to remove is given by ``self.column``.

        Args:
            data (DataFrame): The data to transform. Not guaranteed
                immutable.

        Returns:
            DataFrame: The transformed data.

        """
        return data.drop(self.column, axis=1)


@operation('column-rename')
class ColumnRenameOperation:
    """Rename a specified column in the dataset.

    Expects a ``dict`` as loaded from OpenRefine JSON script.

    Args:
        parameters['description'] (str): Human-readable description
        parameters['oldColumnName'] (str): Column to rename
        parameters['newColumnName'] (str): New name for column
    """

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.transform = {parameters['oldColumnName']:
                          parameters['newColumnName']}

    def execute(self, data):
        """Execute the operation.

        Args:
            data (DataFrame): The data to transform. Not guaranteed
                immutable.

        Returns:
            DataFrame: The transformed data.

        """
        return data.rename(columns=self.transform)


@operation('column-move')
class ColumnMoveOperation:
    """Move a specified column to a different position."""

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.index = parameters['index']

    def execute(self, data):
        """Execute the operation.

        Args:
            data (DataFrame): The data to transform. Not guaranteed
                immutable.

        Returns:
            DataFrame: The transformed data.

        Raises:
            :exc:`IndexError`: If the target column index is less than 0 or
                past the last column.
            :exc:`KeyError`: If the column to be moved is not found.

        """
        cols = list(data.columns)

        if not (0 <= self.index < len(cols)):
            raise IndexError("Target column {} outside range (0, {})"
                             .format(self.index, len(cols) - 1))
        if self.column not in cols:
            raise KeyError("Column '{}' not found in {}"
                           .format(self.column, cols))

        cols.remove(self.column)
        cols.insert(self.index, self.column)

        return data[cols]
