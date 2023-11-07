#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sampling chemical libraries to get random compounds
"""

import time
import argparse
from pathlib import Path
from datetime import timedelta
from multiprocessing import cpu_count

import MolIO
import vstool

parser = argparse.ArgumentParser(prog='docking', description=__doc__.strip())
parser.add_argument('library', help="Path to a directory contains prepared ligand libraries", type=vstool.check_dir)
parser.add_argument('percent', help="Percentage of random compounds need to sample", type=float)
parser.add_argument('--outdir', help="Path to output directory for saving SDF files", type=vstool.mkdir)
parser.add_argument('--extension', help="Extension of prepare ligand library files, default: %(default)s",
                    default='.sdf.gz')

parser.add_argument('--receptor', help="Path to prepared rigid receptor in .pdbqt format file", type=vstool.check_file)
parser.add_argument('--center', help="The X, Y, and Z coordinates of the center", type=float, nargs='+')
parser.add_argument('--size', help="The size in the X, Y, and Z dimension (Angstroms)",
                    type=int, nargs='*', default=[15, 15, 15])

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
logger = vstool.setup_logger(verbose=True)


def sampling(sdf, percent=1, outdir=None):
    output = outdir / sdf.name
    if output.exists():
        logger.debug(f'Output {output} already exists, skip re-sampling')
    else:
        start = time.time()
        logger.debug(f'Sampling {sdf} ...')
        MolIO.sample_sdf(sdf, output, p=percent)
        t = str(timedelta(seconds=time.time() - start))
        logger.debug(f'Sampling {sdf} complete in {t.split(".")[0]}\n')
    return output
    

def main():
    ligands = list(args.library.glob(f'*{args.extension}'))
    processes = min(len(ligands), cpu_count())

    logger.debug(f'Sampling {len(ligands):,} libraries ...')
    outs = vstool.parallel_cpu_task(sampling, ligands, percent=args.percent, outdir=args.outdir, processes=processes)
    logger.debug(f'Sampling {len(ligands):,} libraries complete.')

    if outs and args.receptor:
        cmds = []
        (cx, cy, cz), (sx, sy, sz) = args.center, args.size
        for out in outs:
            cmd = f'docking {out} {args.receptor} --center {cx} {cy} {cz} --size {sx} {sy} {sz}'
            if args.debug:
                cmd = f'{cmd} --debug'
            cmds.append(cmd)

        output = args.outdir / 'docking.commands.txt'
        with open(output, 'w') as o:
            o.writelines(f'{cmd}\n' for cmd in cmds)
            logger.debug(f'Successfully saved {len(cmds):,} docking commands to {output}')


if __name__ == '__main__':
    main()
