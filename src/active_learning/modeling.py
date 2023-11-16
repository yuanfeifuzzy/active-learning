#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command line tool for easily perform model training
"""

import argparse
from pathlib import Path

import cmder
import pandas as pd
import vstool

parser = argparse.ArgumentParser(prog='modeling', description=__doc__.strip())
parser.add_argument('score', help="Path to a CSV file contains SMILES and predicted docking scores", type=vstool.check_file)
parser.add_argument('--percent', help="Percentage of top docking poses need to extract, default: %(default)s",
                    default=0.1, type=float, required=True)
parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
logger = vstool.setup_logger(verbose=True)
root = Path(__file__).parent
setattr(args, 'outdir', vstool.mkdir(args.outdir or args.score.parent / 'model'))
    

def main():
    df = pd.read_csv(args.score)
    df = df.sort_values(by=['score'], ascending=True)
    n = int(df.shape[0] * args.percent * 2 / 100)
    


if __name__ == '__main__':
    main()
