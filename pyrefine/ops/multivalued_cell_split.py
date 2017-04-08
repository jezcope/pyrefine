from .base import Operation


class MultivaluedCellSplitOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.separator = parameters['separator']

    def transform(self, value):
        if self.separator in value:
            return list(map(str.strip, value.split(self.separator)))
        else:
            return [value]

    def execute(self, data):
        try:
            return data.assign(**{self.column:
                                  data[self.column].apply(self.transform)})
        except AttributeError:
            raise TypeError('Non-string data found in column "{}"'
                            .format(self.column))
