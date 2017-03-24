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
