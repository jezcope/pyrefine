"""Operations that operate on whole columns.

.. autosummary::

    ColumnRemovalOperation
    ColumnRenameOperation
"""
from .base import Operation


class ColumnRemovalOperation(Operation):
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


class ColumnRenameOperation(Operation):
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
