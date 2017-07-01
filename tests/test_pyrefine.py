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

from tempfile import mktemp
import pandas as pd
import pandas.util.testing as pdt

from .utils import FIXTURES_PATH

import pyrefine
from pyrefine import cli


@pytest.fixture
def doaj_data_filename():
    return str(FIXTURES_PATH / 'doaj-article-sample.csv')


@pytest.fixture
def doaj_data(doaj_data_filename):
    return pd.read_csv(doaj_data_filename)


@pytest.fixture
def doaj_data_clean_filename():
    return str(FIXTURES_PATH / 'doaj-article-sample-cleaned.csv')



@pytest.fixture
def doaj_data_clean(doaj_data_clean_filename):
    return pd.read_csv(doaj_data_clean_filename)


@pytest.fixture
def doaj_script_filename():
    return str(FIXTURES_PATH / 'doaj-article-clean.json')


@pytest.fixture
def doaj_script(doaj_script_filename):
    with open(doaj_script_filename) as f:
        return f.read()


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

        with open(doaj_data_clean_filename) as f:
            expected_data = f.read()

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
        with open(doaj_data_clean_filename) as f:
            expected_data = f.read()

        assert result.exit_code == 0
        with open(out_file) as f:
            actual_data = f.read()
        assert actual_data == expected_data


class TestScript:

    def test_load_file_object(self):
        with open(FIXTURES_PATH / 'example_script.json') as f:
            script = pyrefine.load_script(f)

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_file_name_string(self):
        script = pyrefine.load_script(str(FIXTURES_PATH) + '/example_script.json')

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_pathlib_path(self):
        script = pyrefine.load_script(FIXTURES_PATH / 'example_script.json')

        assert script is not None
        assert isinstance(script, pyrefine.Script)

    def test_load_string(self):
        with open(FIXTURES_PATH / 'example_script.json') as f:
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
