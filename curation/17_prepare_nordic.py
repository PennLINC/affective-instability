"""Prepare data for NORDIC."""

import os
from glob import glob


def list_files(in_dir):
    """List files in the input directory to run NORDIC on."""
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
    """List files to run NORDIC on.

    This script writes out a file (files_to_nordic.txt) that lists each magnitude BOLD file without
    a NORDIC-denoised counterpart.

    Since CUBIC's MATLAB license limits the number of jobs that can be run at once,
    I run this script once to generate the list of files to run NORDIC on, then submit a job
    to run NORDIC on each file in the list.
    Once that finishes, some of the sub-jobs will have failed because of the license,
    so I run this script again to generate a new list of files to run NORDIC on, and so on,
    until all files have been processed.
    """
    code_dir = "/cbica/projects/pafin/code"
    in_dir = "/cbica/projects/pafin/dset"
    mag_files_to_process = list_files(in_dir)
    with open("files_to_nordic.txt", "w") as fo:
        fo.write("\n".join(mag_files_to_process))
