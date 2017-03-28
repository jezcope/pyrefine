from .base import Operation


class MultivalueCellSplitOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']


Operation.register('core/multivalued-cell-split', MultivalueCellSplitOperation)
