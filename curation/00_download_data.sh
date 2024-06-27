#!/bin/bash
subjects=""
token=$(</cbica/home/salot/tokens/flywheel.txt)
fw login "$token"
cd "/cbica/home/salot/datasets/pafin/sourcedata" || exit

for subject in $subjects; do
    fw download --yes --zip "fw://bbl/CSDSIvsABCD/${subject}"
done
