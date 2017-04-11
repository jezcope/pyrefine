Usage
=====

To use PyRefine from the commandline:

.. code-block:: shell

    $ pyrefine execute script.json input.csv -o output.csv

To use PyRefine in a Python script::

    import pyrefine
    import pandas as pd

    with open('script.json') as script_file:
        script = pyrefine.parse(script_file)

    input_data = pd.read_csv('input.csv')
    output_data = script.execute(input_data)

    # Do something cool with output_data
