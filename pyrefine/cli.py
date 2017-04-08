# -*- coding: utf-8 -*-

import click
import pandas as pd
from .script import parse


@click.group()
def main(args=None):
    """Console script for pyrefine"""
    pass

@main.command()
@click.argument('script', type=click.File('r'))
@click.argument('data', type=click.File('r'))
@click.option('--outfile', '-o', default='-', type=click.File('w'))
def execute(script, data, outfile):
    """Execute a JSON script against a CSV data file"""
    parsed = parse(script.read())
    input_data = pd.read_csv(data)
    output_data = parsed.execute(input_data)
    output_data.to_csv(outfile, index=False)

if __name__ == "__main__":
    main()
