from .base import Operation


class MultivaluedCellJoinOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']

    def transform(self, value):
        return self.separator.join(value)

    def execute(self, data):
        try:
            return data.assign(**{self.column:
                                  data[self.column].apply(self.transform)})
        except AttributeError:
            raise TypeError('Non-string data found in column "{}"'
                            .format(self.column))


Operation.register('core/multivalued-cell-join',
                   MultivaluedCellJoinOperation)
