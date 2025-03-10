"""Clean NaN values from physio data."""

import os
from glob import glob

import numpy as np
import pandas as pd


def clean_file(physio_file):
    print(f"Cleaning {os.path.basename(physio_file)}")
    data = np.loadtxt(physio_file)
    squeeze = False
    if data.ndim == 1:
        data = data[:, np.newaxis]
        squeeze = True

    df = pd.DataFrame(data)
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    data = df.to_numpy()
    if squeeze:
        data = np.squeeze(data)

    np.savetxt(physio_file, data)


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/dset"
    physio_files = glob(os.path.join(in_dir, "sub-*", "ses-1", "func", "*_physio.tsv.gz"))
    for physio_file in physio_files:
        clean_file(physio_file)
