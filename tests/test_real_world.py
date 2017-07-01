# Tests based on real-world examples of usage

import pytest
import pandas as pd
import pandas.util.testing as pdt

from .utils import FIXTURES_PATH

import pyrefine


def assert_script_runs(input_filename, expected_filename, script_filename):
    input_data = pd.read_csv(FIXTURES_PATH / input_filename)
    expected_data = pd.read_csv(FIXTURES_PATH / expected_filename)
    script = pyrefine.load_script(FIXTURES_PATH / script_filename)

    actual_data = script.execute(input_data)

    pdt.assert_frame_equal(actual_data, expected_data)


def test_workshop_script():
    assert_script_runs('workshops-raw.csv',
                       'workshops-clean.csv',
                       'workshops-clean.json')
