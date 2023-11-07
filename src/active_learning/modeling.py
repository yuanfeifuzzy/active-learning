#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command line tool for easily perform model training
"""

import argparse
from pathlib import Path

import cmder

parser = argparse.ArgumentParser(prog='modeling', description=__doc__.strip())
parser.add_argument('score', help="Path to a CSV file contains SMILES and docking scores", type=vstool.check_file)
parser.add_argument('outdir', help="Path to a output directory for saving modeling results", type=vstool.mkdir)

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
logger = vstool.setup_logger(verbose=True)
root = Path(__file__).parent
    

def main():
    cmd = (f'{root}/train.sh --data_path {args.score} --dataset_type regression --save_dir {args.outdir} --quiet '
           f'&> {args.outdir}/modeling.log')
    cmder.run(cmd)


if __name__ == '__main__':
    main()
