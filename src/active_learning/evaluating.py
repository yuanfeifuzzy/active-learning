#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command line tool for easily perform model evaluation
"""

import argparse
from pathlib import Path

import cmder

parser = argparse.ArgumentParser(prog='evaluating', description=__doc__.strip())
parser.add_argument('wd', help="Path to a directory contains SMILES files", type=vstool.check_dir)
parser.add_argument('model', help="Path to a directory contains model checkpoints", type=vstool.check_dir)

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
logger = vstool.setup_logger(verbose=True)


def predict(smile):
    out = smiles.with_suffix('.predict.smiles.score.csv')
    if out.exists():
        logger.debug(f'Predicting result {out} already exists, skip re-predicting')
    else:
        cmd = f'predict.sh --test_path {smile} --checkpoint_dir {args.model} --preds_path {out} --quiet'
        cmder.run(cmd)

def main():
    output = args.wd / 'predict.smiles.score.csv'
    if output.exists():
        logger.debug(f'Modeling prediction {output} already exists, skip re-processing')
    else:
        ss = list(args.wd.glob('*.smiles'))

        logger.debug(f'Predicting docking scores ...')
        vstool.parallel_cpu_task(predict, ss)
        logger.debug(f'Predicting docking scores complete.')

        cmder.run(f'cat {args.wd}/*.predict.smiles.score.csv > {output}')
        logger.debug(f'Successfully saved predict results to {output}')
