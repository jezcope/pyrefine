"""Operations that operate on individual cell contents.

.. autosummary::

    MassEditOperation
    MultivaluedCellSplitOperation
    MultivaluedCellJoinOperation
"""

from .base import Operation


class MassEditOperation(Operation):
    """Apply a simple substition to a whole column.

    Expects a ``dict`` as loaded from OpenRefine JSON script.

    Args:
        parameters['description'] (str): Human-readable description
        parameters['columnName'] (str): Column to edit
        parameters['edits'] (list): List of edits to make
    """

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.edits = parameters['edits']

    def execute(self, data):
        """Execute the operation.

        Args:
            data (DataFrame): The data to transform. Not guaranteed
                immutable.

        Returns:
            DataFrame: The transformed data.
        """
        for edit in self.edits:
            for replace in edit['from']:
                # TODO: loop/condition order could probably be better
                if data[self.column].dtype == object:
                    data[self.column] = data[self.column] \
                                        .apply(self._transform,
                                               from_val=replace,
                                               to_val=edit['to'])
                else:
                    data.loc[data[self.column] == replace, self.column] \
                        = edit['to']

            if edit['fromBlank']:
                data.loc[data[self.column].isnull(), self.column] \
                    = edit['to']

        return data

    @classmethod
    def _transform(cls, val, from_val, to_val):
        if val == from_val:
            return to_val
        elif type(val) is list:
            return [cls._transform(x, from_val, to_val) for x in val]
        else:
            return val


class MultivaluedCellSplitOperation(Operation):
    """Split string values into lists with a given separator.

    Expects a ``dict`` as loaded from OpenRefine JSON script.

    Args:
        parameters['description'] (str): Human-readable description
        parameters['columnName'] (str): Column to edit
        parameters['separator'] (str): String on which to split values
    """

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']

    def _transform(self, value):
        if self.separator in value:
            return list(map(str.strip, value.split(self.separator)))
        else:
            return [value]

    def execute(self, data):
        """Execute the operation.

        Args:
            data (DataFrame): The data to transform. Not guaranteed
                immutable.

        Returns:
            DataFrame: The transformed data.

        Raises:
            TypeError: If data in the relevant column is not a string.
        """
        try:
            return data.assign(**{self.column:
                                  data[self.column].apply(self._transform)})
        except AttributeError:
            raise TypeError('Non-string data found in column "{}"'
                            .format(self.column))


class MultivaluedCellJoinOperation(Operation):
    """Join lists into single strings with a separator.

    Expects a ``dict`` as loaded from OpenRefine JSON script.

    Args:
        parameters['description'] (str): Human-readable description
        parameters['columnName'] (str): Column to edit
        parameters['separator'] (str): String with which to join values
    """

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']

    def _transform(self, value):
        return self.separator.join(value)

    def execute(self, data):
        """Execute the operation.

        Args:
            data (DataFrame): The data to transform. Not guaranteed
                immutable.

        Returns:
            DataFrame: The transformed data.
        """
        return data.assign(**{self.column:
                              data[self.column].apply(self._transform)})