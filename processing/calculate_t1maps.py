"""Calculate a low-resolution, quantitative T1 map from input files.

Authored by Manuel Taso
Modified by Taylor Salo
Modifications:
- Removed mask
- Used BIDS-ish input files, where the two volumes are in separate files
- Used json files for metadata instead of hardcoding values
"""

import json
import os
from glob import glob

import nibabel as nb
import numpy as np
import scipy


def main(tdp1_file, tdp2_file, tdp2_metadata, out_file):
    """Calculate a low-resolution, quantitative T1 map from input files.

    Parameters
    ----------
    tdp1_file : str
        Path to the first TDP volume
    tdp2_file : str
        Path to the second TDP volume
    tdp2_metadata : dict
        Metadata for the second TDP volume
    out_file : str
        Path to the output T1map file
    """

    tdp1_img = nb.load(tdp1_file)
    tdp1_data = tdp1_img.get_fdata()

    tdp2_img = nb.load(tdp2_file)
    tdp2_data = tdp2_img.get_fdata()

    T1 = np.arange(100, 5010, 10)
    trec = tdp2_metadata["SaturationPulseTime"] * 1000
    TI = tdp2_metadata["InversionTime"] * 1000

    z = (1 - 2 * np.exp(-TI / T1) + np.exp(-trec / T1)) / (1 - np.exp(-trec / T1))

    ratio = tdp2_data / tdp1_data
    ratio[ratio == 0] = np.min(z)
    ratio[ratio >= 1] = np.max(z)
    f = scipy.interpolate.interp1d(z, T1, fill_value="extrapolate")

    t1 = f(ratio)
    t1[np.isnan(t1)] = 0

    t1map_img = nb.Nifti1Image(t1, tdp1_img.affine, tdp1_img.header)
    t1map_img.to_filename(out_file)


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/dset"
    tdp1_files = sorted(glob(os.path.join(in_dir, "sub-*/ses-*/anat/*acq-tr1_TDP.nii.gz")))
    for tdp1_file in tdp1_files:
        tdp2_file = tdp1_file.replace("acq-tr1", "acq-tr2")
        tdp2_metadata_file = tdp2_file.replace(".nii.gz", ".json")
        with open(tdp2_metadata_file, "r") as f:
            tdp2_metadata = json.load(f)

        # TODO: Write the T1map out to a derivatives dataset
        out_file = tdp1_file.replace("TDP.nii.gz", "T1map.nii.gz")
        main(tdp1_file, tdp2_file, tdp2_metadata, out_file)
