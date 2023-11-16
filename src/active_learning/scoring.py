#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parsing docking score and preparing input for modeling
"""

import argparse
from pathlib import Path

import cmder
import MolIO
import vstool
from rdkit import Chem

parser = argparse.ArgumentParser(prog='scoring', description=__doc__.strip())
parser.add_argument('wd', help="Path to a directory contains docking output", type=vstool.check_dir)

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
logger = vstool.setup_logger(verbose=True)


def parse(sdf):
    logger.debug(f'Paring {sdf} ...')
    out = sdf.with_suffix('.csv')
    ss = []
    with Chem.SDMolSupplier(str(sdf), removeHs=False) as f:
        for mol in f:
            if mol:
                try:
                    s = Chem.MolToSmiles(mol)
                    score, title = mol.GetProp('score'), mol.GetProp('_Name')
                    ss.append(f'{s},{title},{score}')
                except Exception as e:
                    logger.error(f'Failed to convert mol to SMILES and get score due to {e}')
    if ss:
        with open(out, 'w') as o:
            o.writelines(f'{s}\n' for s in ss)
        logger.debug(f'Successfully saved {len(ss):,} SMILES and scores to {out}')
    return out
    

def main():
    output = args.wd / 'train.smiles.score.csv'
    if output.exists():
        logger.debug(f'Modeling input {output} already exists, skip re-processing')
    else:
        outs = list(args.wd.glob('*.docking.sdf'))

        logger.debug(f'Getting docking poses and scores ...')
        vstool.parallel_cpu_task(parse, outs)
        logger.debug(f'Getting docking poses and scores complete.')

        cmder.run(f'cat smiles,title,score > {output}', exit_on_error=True)
        cmder.run(f'cat {args.wd}/*.csv >> {output}', exit_on_error=True)
        logger.debug(f'Successfully saved SMILES and scores to {output}')


if __name__ == '__main__':
    main()
