from .base import Operation


class ColumnRemovalOperation(Operation):
    """Remove the given column from the dataset."""

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']

    def execute(self, data):
        return data.drop(self.column, axis=1)


class ColumnRenameOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.transform = {parameters['oldColumnName']:
                          parameters['newColumnName']}

    def execute(self, data):
        return data.rename(columns=self.transform)
