#!/bin/bash

# Run heudiconv on the first session
declare -a subses1=("")
for sub in "${subses1[@]}"
do
    echo "$sub"
    heudiconv \
        -f reproin \
        -o /cbica/home/salot/datasets/pafin/dset \
        -d "/cbica/home/salot/datasets/pafin/sourcedata/{subject}_{session}/*/*/*/*.dcm" \
        -s "$sub" \
        -ss 1 \
        --bids
done
