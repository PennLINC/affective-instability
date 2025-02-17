#!/bin/bash
/cbica/projects/pafin/miniforge3/envs/curation/bin/heudiconv -f /cbica/projects/pafin/code/curation/heuristic.py -o /cbica/projects/pafin/dset -d /cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353/{subject}_*/*/*/*/*.dcm --subjects PILOT02 --ses 1 --bids
