#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyrefine
----------------------------------

Tests for `pyrefine` module.
"""

import pytest

# from contextlib import contextmanager
from click.testing import CliRunner

import os.path
import pandas as pd
import numpy as np
import pandas.util.testing as pdt

import pyrefine
from pyrefine import cli


@pytest.fixture
def doaj_data():
    filename = os.path.join(os.path.dirname(__file__),
                            'fixtures/doaj-article-sample.csv')
    return pd.read_csv(filename)


@pytest.fixture
def doaj_data_clean():
    filename = os.path.join(os.path.dirname(__file__),
                            'fixtures/doaj-article-sample-cleaned.csv')
    return pd.read_csv(filename)


@pytest.fixture
def doaj_script():
    filename = os.path.join(os.path.dirname(__file__),
                            'fixtures/doaj-article-clean.json')
    return open(filename).read()


@pytest.mark.skip
class TestCLI:

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pyrefine.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output


class TestScript:

    def test_load_file_object(self):
        with open(os.path.dirname(__file__)
                  + '/fixtures/example_script.json') as f:
            script = pyrefine.load_script(f)

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_file_name(self):
        script = pyrefine.load_script(os.path.dirname(__file__)
                                      + '/fixtures/example_script.json')

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_string(self):
        with open(os.path.dirname(__file__)
                  + '/fixtures/example_script.json') as f:
            script_string = f.read()

        script = pyrefine.parse(script_string)

        assert script is not None
        assert isinstance(script, pyrefine.Script)
        assert len(script) == 1

    def test_empty_script(self):
        script = pyrefine.parse("[]")

        assert script is not None
        assert isinstance(script, pyrefine.Script)
        assert len(script) == 0

    @pytest.mark.xfail
    def test_whole_script(self, doaj_data, doaj_data_clean, doaj_script):
        script = pyrefine.parse(doaj_script)

        result = script.execute(doaj_data)

        assert result.equals(doaj_data_clean)


class TestOperation:

    def test_create_no_operation(self):
        with pytest.raises(KeyError):
            pyrefine.ops.Operation.create({})

    def test_create_unknown_action(self):
        with pytest.raises(RuntimeError):
            pyrefine.ops.Operation.create({'op': 'does not exist'})

    def test_create_base_operation(self):
        with pytest.raises(NotImplementedError):
            pyrefine.ops.Operation()


class TestMassEditOperation:

    @pytest.fixture
    def default_params(self):
        return {'columnName': 'needs_fixing',
                'description': 'Test mass edit',
                'edits': [{'from': ['wrong'],
                           'fromBlank': False,
                           'fromError': False,
                           'to': 'right'}],
                'engineConfig': {'facets': [], 'mode': 'row-based'},
                'expression': 'value',
                'op': 'core/mass-edit'}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({
            'other': 'one two three four five'.split(),
            'needs_fixing': ['wrong', 'right', 'wrong', 'questionable',
                             None],
            'age': np.random.randint(18, 70, 5)})

    def test_create_valid_params(self, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        assert action is not None
        assert isinstance(action, pyrefine.ops.MassEditOperation)

    def test_single_edit(self, base_data, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        expected_data = base_data.copy()
        expected_data.needs_fixing = ['right', 'right', 'right',
                                      'questionable', None]

        actual_data = action.execute(base_data)

        pdt.assert_frame_equal(expected_data, actual_data)

    def test_multiple_edits(self, base_data, default_params):
        parameters = dict(default_params,
                          edits=[{'from': ['wrong'],
                                  'fromBlank': False,
                                  'fromError': False,
                                  'to': 'right'},
                                 {'from': ['questionable'],
                                  'fromBlank': False,
                                  'fromError': False,
                                  'to': '?'}])
        action = pyrefine.ops.Operation.create(parameters)

        expected_data = base_data.copy()
        expected_data.needs_fixing = ['right', 'right', 'right', '?', None]

        actual_data = action.execute(base_data)

        pdt.assert_frame_equal(expected_data, actual_data)

    def test_fromblank_edit(self, base_data, default_params):
        parameters = dict(default_params,
                          edits=[{'from': [],
                                  'fromBlank': True,
                                  'fromError': False,
                                  'to': 'not blank'}])
        action = pyrefine.ops.Operation.create(parameters)

        expected_data = base_data.copy()
        expected_data.needs_fixing = ['wrong', 'right', 'wrong',
                                      'questionable', 'not blank']

        actual_data = action.execute(base_data)

        pdt.assert_frame_equal(expected_data, actual_data)

    def test_multivalued_cell(self, base_data, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        base_data.needs_fixing = ['wrong', 'right',
                                  ['wrong', 'foo bar', 'baz', 'wrong'],
                                  'questionable', ['right', 'wrong']]
        expected_data = base_data.copy()
        expected_data.needs_fixing = ['right', 'right',
                                      ['right', 'foo bar', 'baz', 'right'],
                                      'questionable', ['right', 'right']]

        actual_data = action.execute(base_data)

        pdt.assert_frame_equal(expected_data, actual_data)


class TestMultivaluedCellSplitOperation:

    @pytest.fixture
    def default_params(self):
        return {"op": "core/multivalued-cell-split",
                "description": "Split multi-valued cells in column split_me",
                "columnName": "split_me",
                "keyColumnName": "Title",
                "separator": "|",
                "mode": "plain"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(3),
                             'split_me': ['Split|these|up',
                                          'No splitting here',
                                          'Item 1|item 2|item_3']})

    def test_create_valid_params(self, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        assert action is not None
        assert isinstance(action, pyrefine.ops.MultivaluedCellSplitOperation)

    def test_split_column(self, default_params, base_data):
        action = pyrefine.ops.Operation.create(default_params)

        expected_data = base_data.copy()
        expected_data.split_me = [['Split', 'these', 'up'],
                                  ['No splitting here'],
                                  ['Item 1', 'item 2', 'item_3']]

        actual_data = action.execute(base_data)

        assert actual_data.equals(expected_data)

    def test_split_numeric_column(self, default_params, base_data):
        parameters = dict(default_params,
                          columnName='id')

        action = pyrefine.ops.Operation.create(parameters)

        with pytest.raises(TypeError):
            action.execute(base_data)


class TestMultivaluedCellJoinOperation:

    @pytest.fixture
    def default_params(self):
        return {"op": "core/multivalued-cell-join",
                "description": "Join multi-valued cells in column split_me",
                "columnName": "join_me",
                "keyColumnName": "Title",
                "separator": "|",
                "mode": "plain"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(3),
                             'join_me': [['Join', 'these', 'up'],
                                         ['No splitting here'],
                                         ['Item 1', 'item 2', 'item_3']]})

    def test_create_valid_params(self, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        assert action is not None
        assert isinstance(action, pyrefine.ops.MultivaluedCellJoinOperation)

    def test_split_column(self, default_params, base_data):
        action = pyrefine.ops.Operation.create(default_params)

        expected_data = base_data.copy()
        expected_data.join_me = ['Join|these|up',
                                 'No splitting here',
                                 'Item 1|item 2|item_3']

        actual_data = action.execute(base_data)

        assert actual_data.equals(expected_data)

    def test_split_numeric_column(self, default_params, base_data):
        parameters = dict(default_params,
                          columnName='id')

        action = pyrefine.ops.Operation.create(parameters)

        with pytest.raises(TypeError):
            action.execute(base_data)


class TestColumnRemovalOperation:

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-removal",
                "description": "Remove column remove_me",
                "columnName": "remove_me"}

    def test_create_valid_params(self, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        assert action is not None
        assert isinstance(action, pyrefine.ops.ColumnRemovalOperation)

    def test_remove_column(self, default_params):
        base_data = pd.DataFrame({'keep_me': np.arange(20),
                                  'remove_me': np.arange(20)})

        action = pyrefine.ops.Operation.create(default_params)
        actual_data = action.execute(base_data)

        assert 'remove_me' not in actual_data.columns
        assert 'keep_me' in actual_data.columns


class TestColumnRenameOperation:

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-rename",
                "description": "Rename column oldname to blah",
                "oldColumnName": "oldname",
                "newColumnName": "blah"}

    def test_create_valid_params(self, default_params):
        action = pyrefine.ops.Operation.create(default_params)

        assert action is not None
        assert isinstance(action, pyrefine.ops.ColumnRenameOperation)

    def test_remove_column(self, default_params):
        base_data = pd.DataFrame({'keep_me': np.arange(20),
                                  'oldname': np.arange(20)})

        action = pyrefine.ops.Operation.create(default_params)
        actual_data = action.execute(base_data)

        assert 'oldname' not in actual_data.columns
        assert 'blah' in actual_data.columns
        assert actual_data.blah.equals(base_data.oldname)
