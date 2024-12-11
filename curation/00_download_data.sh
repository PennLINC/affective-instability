#!/bin/bash
unset LD_LIBRARY_PATH

subjects="PILOT01_techdev PILOT02_techdev 24630_13104"
token=$(</cbica/projects/pafin/tokens/flywheel.txt)
~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw login "$token"
cd "/cbica/projects/pafin/sourcedata/imaging" || exit

for subject in $subjects; do
    ~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw download --yes --zip "fw://bbl/PAFIN_844353/${subject}"
done
