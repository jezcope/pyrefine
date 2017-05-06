"""Operations that operate on individual cell contents.

.. autosummary::

    MassEditOperation
    MultivaluedCellSplitOperation
    MultivaluedCellJoinOperation
"""

from .base import operation


@operation('mass-edit')
class MassEditOperation:
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
            data (DataFrame): The data to transform.

        Returns:
            DataFrame: The transformed data.

        """
        column_data = data[self.column].copy()
        if data[self.column].dtype == object:
            do_replace = self._do_replace_object
        else:
            do_replace = self._do_replace

        for edit in self.edits:
            for from_val in edit['from']:
                column_data = do_replace(column_data, from_val, edit['to'])

            if edit['fromBlank']:
                column_data[column_data.isnull()] = edit['to']

        return data.assign(**{self.column: column_data})

    @classmethod
    def _do_replace(cls, column, from_val, to_val):
        column[column == from_val] = to_val
        return column

    @classmethod
    def _do_replace_object(cls, column, from_val, to_val):
        return column.apply(cls._transform,
                            from_val=from_val, to_val=to_val)

    @classmethod
    def _transform(cls, val, from_val, to_val):
        if val == from_val:
            return to_val
        elif type(val) is list:
            return [cls._transform(x, from_val, to_val) for x in val]
        else:
            return val


@operation('blank-down')
class BlankDownOperation:
    """Blank down repeated values.

    Expects a ``dict`` as loaded from OpenRefine JSON script.

    Args:
        parameters['description'] (str): Human-readable description
        parameters['columnName'] (str): Column to edit
    """

    def __init__(self, parameters):
        """Initialise the operation."""
        self.description = parameters['description']
        self.column = parameters['columnName']

    def execute(self, data):
        """Execute the operation.

        Args:
            data (DataFrame): The data to transform.

        Returns:
            DataFrame: The transformed data.

        Raises:
            TypeError: If data in the relevant column is not a string.

        """
        new_column = data[self.column].copy()
        last_val = None

        for i, val in enumerate(new_column):
            if val == last_val:
                new_column[i] = None
            else:
                last_val = val

        return data.assign(**{self.column: new_column})



@operation('multivalued-cell-split')
class MultivaluedCellSplitOperation:
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
            data (DataFrame): The data to transform.

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


@operation('multivalued-cell-join')
class MultivaluedCellJoinOperation:
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
            data (DataFrame): The data to transform.

        Returns:
            DataFrame: The transformed data.

        """
        return data.assign(**{self.column:
                              data[self.column].apply(self._transform)})
