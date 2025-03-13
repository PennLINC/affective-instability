"""
Run peakdet on all physio files in the dataset.

This script will identify peaks and troughs in the physio data and save the results
in the derivatives/physiopy directory.
"""

import json
import os
from glob import glob

import matplotlib.pyplot as plt
from peakdet import load_physio, operations


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/dset"
    out_dir = "/cbica/projects/pafin/derivatives/physiopy"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "figures"), exist_ok=True)

    physio_files = glob(os.path.join(in_dir, "sub-*", "ses-1", "func", "*_physio.tsv.gz"))
    for physio_file in physio_files:
        if "trigger" in physio_file:
            print(f"Skipping {physio_file} because it contains 'trigger'")
            continue

        json_file = physio_file.replace(".tsv.gz", ".json")

        with open(json_file) as fo:
            metadata = json.load(fo)

        fs = metadata["SamplingFrequency"]

        data = load_physio(physio_file, fs=fs)
        data = operations.filter_physio(data, cutoffs=1, method="lowpass")
        data = operations.peakfind_physio(data, thresh=0.1, dist=100)

        fig, axes = plt.subplots(figsize=(16, 24), nrows=10, sharey=True)
        for i_ax, ax in enumerate(axes):
            operations.plot_physio(data, ax=ax)
            ax_start = i_ax * 50
            ax_end = (i_ax + 1) * 50
            ax.set_xlim(ax_start, ax_end)

        fig.suptitle(os.path.basename(physio_file).replace("_physio.tsv.gz", ""))
        fig.tight_layout()
        fig.savefig(
            os.path.join(
                out_dir,
                "figures",
                os.path.basename(physio_file).replace("_physio.tsv.gz", "_peakdet.png"),
            ),
        )
