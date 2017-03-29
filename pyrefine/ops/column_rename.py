from .base import Operation


class ColumnRenameOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.transform = {parameters['oldColumnName']:
                          parameters['newColumnName']}

    def execute(self, data):
        return data.rename(columns=self.transform)


Operation.register('core/column-rename', ColumnRenameOperation)
