#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sampling chemical libraries to get random compounds
"""

import os
import time
import argparse
from pathlib import Path
from datetime import timedelta
from multiprocessing import cpu_count

import MolIO
import vstool

parser = argparse.ArgumentParser(prog='active-learning', description=__doc__.strip())
parser.add_argument('library', help="Path to a directory contains prepared ligand libraries", type=vstool.check_dir)
parser.add_argument('receptor', help="Path to prepared rigid receptor in .pdbqt format file", type=vstool.check_file)
parser.add_argument('--percent', help="Percentage of random compounds need to sample, default: %(default)s",
                    default=1, type=float)
parser.add_argument('--center', help="The X, Y, and Z coordinates of the center", type=float, nargs='+')
parser.add_argument('--size', help="The size in the X, Y, and Z dimension (Angstroms)",
                    type=int, nargs='*', default=[15, 15, 15])
parser.add_argument('--outdir', help="Path to output directory for saving result files", type=vstool.mkdir)
parser.add_argument('--scratch', help="Path to the scratch directory, default: %(default)s",
                        default=os.environ.get('SCRATCH', '/scratch'))
parser.add_argument('--extension', help="Extension of prepare ligand library files, default: %(default)s",
                    default='.sdf.gz')

parser.add_argument('--nodes', type=int, default=8, help="Number of nodes, default: %(default)s.")
parser.add_argument('--project', help='The nmme of project you would like to be charged')
parser.add_argument('--queue', help='The nmme of queue you would like to submit', default='gpu-a100')
parser.add_argument('--email', help='Email address for send status change emails')
parser.add_argument('--email-type', help='Email type for send status change emails, default: %(default)s',
                    default='ALL', choices=('NONE', 'BEGIN', 'END', 'FAIL', 'REQUEUE', 'ALL'))
parser.add_argument('--delay', help='Hours need to delay running the job.', type=int, default=0)

parser.add_argument('--debug', help='Enable debug mode (for development purpose).', action='store_true')
parser.add_argument('--version', version=vstool.get_version(__package__), action='version')

args = parser.parse_args()
logger = vstool.setup_logger(verbose=True)

    

def main():
    setattr(args, 'scratch', vstool.mkdir(f'{args.scratch}/{args.outdir.name}'))
    setattr(args, 'nodes', 2 if args.debug else args.nodes)

    wd, queue = str(args.scratch), args.queue
    if 'a100' in queue:
        ntasks_per_node = 3
    elif 'h100' in queue:
        ntasks_per_node = 2
    elif 'rtx' in queue:
        ntasks_per_node = 4
    else:
        raise ValueError(f'Invalid queue {queue}')

    ntasks = args.nodes * ntasks_per_node

    source = f'source {Path(vstool.check_exe("python")).parent}/activate'
    cd = f'cd {args.outdir} || {{ echo "Failed to cd into {args.outdir}!"; exit 1; }}\n'

    (cx, cy, cz), (sx, sy, sz) = args.center, args.size
    sampling = ['sampling', str(args.library), str(args.percent), f'--outdir {wd}',
                f'--extension {args.extension}', f'--receptor {args.receptor}',
                f'--center {cx} {cy} {cz}', f'--size {sx} {sy} {sz}', '--debug']
    sampling = ' \\\n  '.join(sampling) + '\n'

    docking = ['module load launcher_gpu', f'export LAUNCHER_WORKDIR={wd}',
               f'export LAUNCHER_JOB_FILE={wd}/docking.commands.txt', '',
               '${{LAUNCHER_DIR}}/paramrun', '']
    docking = '\n'.join(docking)

    scoring = f'scoring {wd} --debug'
    modeling = f'modeling {wd}/train.smiles.score.csv {args.scratch}/model --debug'
    evaluating = f'evaluating {wd} {wd}/model --debug'

    cmd = '\n'.join([source, cd, sampling, docking, scoring, modeling, evaluating])
    vstool.submit(cmd, nodes=args.nodes, ntasks=ntasks, ntasks_per_node=ntasks_per_node,
                  job_name='ACL', day=0 if args.debug else 1, hour=1 if args.debug else 23,
                  minute=59, partation=queue, email=args.email, mail_type=args.email_type,
                  log='learning.log', script=args.outdir / 'submit.sh', delay=args.delay,
                  project=args.project)


if __name__ == '__main__':
    main()
