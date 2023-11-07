#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command line tool for easily perform ligand-protein docking with Uni-Dock
"""

import os
import sys
import argparse
import traceback
from pathlib import Path

import cmder
import MolIO
import vstool

parser = argparse.ArgumentParser(prog='docking', description=__doc__.strip())
parser.add_argument('ligand', help="Path to a SDF file contains prepared ligands", type=vstool.check_file)
parser.add_argument('receptor', help="Path to prepared rigid receptor in .pdbqt format file", type=vstool.check_file)
parser.add_argument('--center', help="The X, Y, and Z coordinates of the center", type=float, nargs='+')
parser.add_argument('--size', help="The size in the X, Y, and Z dimension (Angstroms)",
                    type=int, nargs='*', default=[15, 15, 15])

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
vstool.setup_logger(verbose=True)


def ligand_list(sdf):
    logger.debug(f'Parsing {sdf} into individual files')
    output = Path(sdf).with_suffix('.txt')
    ligands, outdir = [], Path(sdf).parent

    for ligand in MolIO.parse_sdf(sdf):
        out = ligand.sdf(output=outdir / f'{ligand.title}.sdf')
        if out:
            ligands.append(out)
            if args.debug and len(ligands) == 100:
                logger.debug(f'Debug mode enabled, only first 100 ligands passed filters in {sdf} were saved')
                break

    with output.open('w') as o:
        o.writelines(f'{ligand}\n' for ligand in ligands)
    return output, ligands


def unidock(batch):
    logger.debug(f'Docking ligands in {batch} ...')
    (cx, cy, cz), (sx, sy, sz) = args.center, args.size
    cmd = (f'{args.exe} --receptor {args.receptor} '
           f'--ligand_index {batch} --search_mode balance --scoring vina --max_gpu_memory 16000 '
           f'--center_x {cx} --center_y {cy} --center_z {cz} --size_x {sx} --size_y {sy} --size_z {sz} '
           f'--dir {Path(batch).parent} &> /dev/null')

    cmder.run(cmd)
    logger.debug(f'Docking ligands in {batch} complete.\n')


def best_pose(sdf):
    ss, out = [], Path(f'{Path(sdf).with_suffix("")}_out.sdf')
    if out.exists():
        for s in MolIO.parse(str(out)):
            if s.mol and s.score < 0:
                ss.append(s)
                
        if not args.debug:
            os.unlink(sdf)
            os.unlink(out)

    ss = sorted(ss, key=lambda x: x.score)[0] if ss else None
    return ss


def main():
    batch, ligands = ligand_list(args.ligand)
    unidock(batch)
    
    logger.debug(f'Getting docking poses and scores ...')
    poses = vstool.parallel_cpu_task(best_pose, ligands)
    logger.debug(f'Getting docking poses and scores complete.')
    
    if poses:
        output = str(args.ligand.with_suffix('.docking.sdf'))
        logger.debug(f'Saving poses to {output} ...')
        MolIO.write(poses, output)
        logger.debug(f'Successfully saved {len(poses):,} poses to {output}.\n')


if __name__ == '__main__':
    main()
