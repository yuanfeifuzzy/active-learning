#!/usr/bin/env bash

venv=/work/08944/fuzzy/share/software/chemprop/venv
source ${venv}/bin/activate
export LD_LIBRARY_PATH="${venv}"/lib/python3.11/site-packages/nvidia/nvjitlink/lib:$LD_LIBRARY_PATH

chemprop_train "$@"

