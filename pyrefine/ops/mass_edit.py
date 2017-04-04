from .base import Operation


class MassEditOperation(Operation):

    def __init__(self, parameters):
        self.description = parameters['description']
        self.column = parameters['columnName']
        self.edits = parameters['edits']

    def execute(self, data):
        for edit in self.edits:
            for replace in edit['from']:
                data.loc[data[self.column] == replace, self.column] \
                    = edit['to']
            if edit['fromBlank']:
                data.loc[data[self.column].isnull(), self.column] \
                    = edit['to']

        return data
