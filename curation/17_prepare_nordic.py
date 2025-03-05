"""Prepare data for NORDIC."""

import os
import subprocess
from glob import glob

import nibabel as nb


def list_files(in_dir):
    """List files in the input directory to process."""
    mag_files = sorted(
        glob(
            os.path.join(
                in_dir,
                "sub-*",
                "ses-*",
                "func",
                "sub-*_bold.nii.gz",
            ),
        ),
    )
    # Don't include phase files
    mag_files = [mf for mf in mag_files if "part-phase" not in mf]

    nordic_mag_files = [mf.replace("_rec-nordic", "") for mf in mag_files if "_rec-nordic" in mf]

    # Don't include NORDIC-denoised files
    mag_files = [mf for mf in mag_files if "_rec-nordic" not in mf]

    mag_files_to_process = [mf for mf in mag_files if mf not in nordic_mag_files]

    return mag_files_to_process


if __name__ == "__main__":
    code_dir = "/cbica/projects/pafin/code"
    in_dir = "/cbica/projects/pafin/dset"
    mag_files_to_process = list_files(in_dir)
    with open("files_to_nordic.txt", "w") as fo:
        fo.write("\n".join(mag_files_to_process))
