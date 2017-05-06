#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyrefine
----------------------------------

Tests for `pyrefine` module.
"""

# flake8: noqa

import pytest

# from contextlib import contextmanager
from click.testing import CliRunner

import os.path
from tempfile import mktemp
import pandas as pd
import numpy as np
import pandas.util.testing as pdt

import pyrefine
from pyrefine import cli


def assert_op_changes_data(params, *, base_data, expected_data):
    op = pyrefine.ops.create(params)
    actual_data = op.execute(base_data)

    pdt.assert_frame_equal(expected_data, actual_data)

def assert_op_raises(params, data, exception):
    op = pyrefine.ops.create(params)
    with pytest.raises(exception):
        op.execute(data)

def print_frame_differing_rows(df1, df2):
    """Print the difference between two :class:`DataFrame`s

    Prints the rows of the two DataFrames which differ, along with a
    boolean DataFrame indicating which individual values differ.

    Args:
        df1, df2 (:class:`pandas.DataFrame`): The two DataFrames to
            compare.
    """
    diff = (df1 == df2) | df1.isnull() | df2.isnull()
    rows = ~(diff.all(axis=1))
    print(df1[rows])
    print(df2[rows])
    print(diff[rows])


@pytest.fixture
def doaj_data_filename():
    return os.path.join(os.path.dirname(__file__),
                        'fixtures/doaj-article-sample.csv')


@pytest.fixture
def doaj_data(doaj_data_filename):
    return pd.read_csv(doaj_data_filename)


@pytest.fixture
def doaj_data_clean_filename():
    return os.path.join(os.path.dirname(__file__),
                        'fixtures/doaj-article-sample-cleaned.csv')


@pytest.fixture
def doaj_data_clean(doaj_data_clean_filename):
    return pd.read_csv(doaj_data_clean_filename)


@pytest.fixture
def doaj_script_filename():
    return os.path.join(os.path.dirname(__file__),
                        'fixtures/doaj-article-clean.json')


@pytest.fixture
def doaj_script(doaj_script_filename):
    return open(doaj_script_filename).read()


class TestCLI:

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pyrefine' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_cli_execute_stdout(self, doaj_script_filename,
                                doaj_data_filename,
                                doaj_data_clean_filename):
        runner = CliRunner()
        result = runner.invoke(cli.execute,
                               [doaj_script_filename, doaj_data_filename])

        expected_data = open(doaj_data_clean_filename).read()

        assert result.exit_code == 0
        assert result.output == expected_data

    def test_cli_execute_outfile(self, doaj_script_filename,
                                 doaj_data_filename,
                                 doaj_data_clean_filename):
        runner = CliRunner()
        out_file = mktemp()
        result = runner.invoke(cli.execute,
                               [doaj_script_filename, doaj_data_filename,
                                '-o', out_file])
        expected_data = open(doaj_data_clean_filename).read()

        assert result.exit_code == 0
        actual_data = open(out_file).read()

        assert actual_data == expected_data


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

    def test_whole_script(self, doaj_data, doaj_data_clean, doaj_script):
        script = pyrefine.parse(doaj_script)

        result = script.execute(doaj_data)

        pdt.assert_frame_equal(result, doaj_data_clean)


class TestOperation:

    def test_create_no_operation(self):
        with pytest.raises(KeyError):
            pyrefine.ops.create({})

    def test_create_unknown_action(self):
        with pytest.raises(RuntimeError):
            pyrefine.ops.create({'op': 'does not exist'})


class CommonOperationTests:

    def test_create_valid_params(self, default_params):
        action = pyrefine.ops.create(default_params)

        assert action is not None
        assert isinstance(action, self.op_class)

    def test_input_immutable(self, default_params, base_data):
        op = pyrefine.ops.create(default_params)
        orig_data = base_data.copy()

        op.execute(base_data)
        pdt.assert_frame_equal(orig_data, base_data)


class TestMassEditOperation(CommonOperationTests):

    op_class = pyrefine.ops.MassEditOperation

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

    def test_single_edit(self, base_data, default_params):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                needs_fixing=['right', 'right', 'right',
                              'questionable', None]))

    def test_single_edit_numeric(self, base_data, default_params):
        assert_op_changes_data(
            dict(default_params,
                 edits=[{'from': [200, 2000],
                         'fromBlank': False,
                         'fromError': False,
                         'to': 20}]),
            base_data=base_data.assign(
                needs_fixing=[123, 78, 200, 20, 2000]),
            expected_data=base_data.assign(
                needs_fixing=[123, 78, 20, 20, 20]))

    def test_multiple_edits(self, base_data, default_params):
        assert_op_changes_data(
            dict(default_params,
                 edits=[{'from': ['wrong'], 'to': 'right',
                         'fromBlank': False, 'fromError': False},
                        {'from': ['questionable'], 'to': '?',
                         'fromBlank': False, 'fromError': False}]),
            base_data=base_data,
            expected_data=base_data.assign(
                needs_fixing=['right', 'right', 'right', '?', None]))

    def test_fromblank_edit(self, base_data, default_params):
        assert_op_changes_data(
            dict(default_params,
                 edits=[{'from': [], 'to': 'not blank',
                         'fromBlank': True,
                         'fromError': False}]),
            base_data=base_data,
            expected_data=base_data.assign(
                needs_fixing=['wrong', 'right', 'wrong',
                              'questionable', 'not blank']))

    def test_multivalued_cell(self, base_data, default_params):
        assert_op_changes_data(
            default_params,
            base_data=base_data.assign(
                needs_fixing=['wrong', 'right',
                              ['wrong', 'foo bar', 'baz', 'wrong'],
                              'questionable', ['right', 'wrong']]),
            expected_data=base_data.assign(
                needs_fixing=['right', 'right',
                              ['right', 'foo bar', 'baz', 'right'],
                              'questionable', ['right', 'right']]))


class TestBlankDownOperation(CommonOperationTests):

    op_class = pyrefine.ops.BlankDownOperation

    @pytest.fixture
    def default_params(self):
        return {"op": "core/blank-down",
                "description": "Blank down cells in column tidy_up",
                "engineConfig": {
                    "mode": "row-based",
                    "facets": []
                },
                "columnName": "tidy_up"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'id': np.arange(10),
                             'tidy_up': ['one', 'two', 'two', 'three', 'four',
                                         'four', 'four', 'four', 'five', 'five']})

    def test_blank_down(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                tidy_up=['one', 'two', None, 'three', 'four',
                         None, None, None, 'five', None]))


class TestMultivaluedCellSplitOperation(CommonOperationTests):

    op_class = pyrefine.ops.MultivaluedCellSplitOperation

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

    def test_split_column(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                split_me=[['Split', 'these', 'up'],
                          ['No splitting here'],
                          ['Item 1', 'item 2', 'item_3']]))

    def test_split_numeric_column(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='id'),
                         base_data, TypeError)

    def test_with_spaces(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data.assign(
                split_me=['This|  has|  some |spaces ',
                          'No splitting here ',
                          'Item 1|item 2|item_3']),
            expected_data=base_data.assign(
                split_me=[['This', 'has', 'some', 'spaces'],
                          ['No splitting here '],
                          ['Item 1', 'item 2', 'item_3']]))


class TestMultivaluedCellJoinOperation(CommonOperationTests):

    op_class = pyrefine.ops.MultivaluedCellJoinOperation

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

    def test_split_column(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=base_data.assign(
                join_me=['Join|these|up',
                         'No splitting here',
                         'Item 1|item 2|item_3']))

    def test_split_numeric_column(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='id'),
                         base_data, TypeError)


class TestColumnRemovalOperation(CommonOperationTests):

    op_class = pyrefine.ops.ColumnRemovalOperation

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-removal",
                "description": "Remove column remove_me",
                "columnName": "remove_me"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'keep_me': np.arange(20),
                             'remove_me': np.arange(20)})

    def test_remove_column(self, default_params, base_data):
        action = pyrefine.ops.create(default_params)
        actual_data = action.execute(base_data)

        assert 'remove_me' not in actual_data.columns
        assert 'keep_me' in actual_data.columns


class TestColumnRenameOperation(CommonOperationTests):

    op_class = pyrefine.ops.ColumnRenameOperation

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-rename",
                "description": "Rename column oldname to blah",
                "oldColumnName": "oldname",
                "newColumnName": "blah"}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame({'keep_me': np.arange(20),
                             'oldname': np.arange(20)})

    def test_remove_column(self, default_params, base_data):
        action = pyrefine.ops.create(default_params)
        actual_data = action.execute(base_data)

        assert 'oldname' not in actual_data.columns
        assert 'blah' in actual_data.columns
        pdt.assert_series_equal(actual_data.blah,
                                base_data.oldname.rename("blah"))


class TestColumnMoveOperation(CommonOperationTests):

    op_class = pyrefine.ops.ColumnMoveOperation

    @pytest.fixture
    def default_params(self):
        return {"op": "core/column-move",
                "description": "Move column third to position 0",
                "columnName": "third",
                "index": 0}

    @pytest.fixture
    def base_data(self):
        return pd.DataFrame(np.eye(4, dtype=int),
                            columns='first second third fourth'.split())

    def test_move_column_to_start(self, default_params, base_data):
        assert_op_changes_data(
            default_params,
            base_data=base_data,
            expected_data=pd.DataFrame([[0, 1, 0, 0],
                                        [0, 0, 1, 0],
                                        [1, 0, 0, 0],
                                        [0, 0, 0, 1]],
                                       columns='third first second fourth'.split()))
    def test_move_column_to_end(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params, columnName='third', index=3),
            base_data=base_data,
            expected_data=pd.DataFrame([[1, 0, 0, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 0, 1],
                                        [0, 0, 1, 0]],
                                       columns='first second fourth third'.split()))

    def test_move_column_to_right(self, default_params, base_data):
        assert_op_changes_data(
            dict(default_params, columnName='second', index=2),
            base_data=base_data,
            expected_data=pd.DataFrame([[1, 0, 0, 0],
                                        [0, 0, 1, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 0, 1]],
                                       columns='first third second fourth'.split()))

    def test_move_column_before_start(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='third', index=-2),
                         base_data, IndexError)

    def test_move_column_after_end(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='third', index=4),
                         base_data, IndexError)

    def test_move_non_existent_column(self, default_params, base_data):
        assert_op_raises(dict(default_params, columnName='seventh', index=2),
                         base_data, KeyError)
