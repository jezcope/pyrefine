from .base import Operation


class ColumnRemovalOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']

    def execute(self, data):
        return data.drop(self.column, axis=1)


Operation.register('core/column-removal', ColumnRemovalOperation)
