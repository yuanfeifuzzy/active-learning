#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command line tool for extracting top docking poses
"""

import argparse
from pathlib import Path

import cmder
import pandas as pd
import vstool

parser = argparse.ArgumentParser(prog='topping', description=__doc__.strip())
parser.add_argument('wd', help="Path to a directory contains prediction results", type=vstool.check_dir)
parser.add_argument('--percent', help="Path to a directory contains prediction results", type=vstool.check_dir)

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
root = Path(__file__).parent
logger = vstool.setup_logger(verbose=True)


def top(smiles):
    out = smiles.parent / 'top.smiles.csv'
    if out.exists():
        logger.debug(f'Top SMILES {out} already exists, skip re-predicting')
        df = pd.read_csv(out)
    else:
        df = pd.read_csv(smiles, usecols=[1, 2])
        df.columns = ['title', 'score']
        df = df.sort_values(by=['score'], ascending=True)
        df = df.head(int(df.shape[0] * args.percent * 2))
        df.to_csv(out, index=False)
    return df


def main():
    output = args.wd / 'top.smiles'
    if output.exists():
        logger.debug(f'Top docking SMILES {output} already exists, skip re-processing')
    else:
        ss = list(args.wd.glob('*.predict.smiles.score.csv'))

        logger.debug(f'Extracting top docking poses ...')
        if len(ss) == 1:
            df = top(ss[0])
        elif len(ss) > 1:
            df = vstool.parallel_cpu_task(top, ss)
            df = pd.concat(df)
        else:
            raise ValueError(f'No predicting results files found in {args.wd}')
        logger.debug(f'Extracting top docking poses complete.')

        df = df.sort_values(by=['score'], ascending=True)
        df = df.head(int(df.shape[0] / 2))
        df.to_csv(out, index=False)