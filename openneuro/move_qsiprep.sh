#!/usr/bin/env bash
set -euo pipefail

in_dir="/cbica/projects/pafin/derivatives/qsirecon2/derivatives/qsirecon-extrapolateDSIQ5"
out_dir="/cbica/projects/pafin/derivatives/qsirecon/derivatives/qsirecon-extrapolateDSIQ5"

for src in "$in_dir"/sub-*; do
  [ -d "$src" ] || continue                    # skip if no matches
  name="${src##*/}"
  if [ -e "$out_dir/$name" ]; then
    echo "Skipping $name (already exists in out_dir)"
    continue
  fi
  mv -- "$src" "$out_dir/"
done

