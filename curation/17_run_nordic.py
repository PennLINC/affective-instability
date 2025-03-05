"""Prepare data for NORDIC."""

import os
import subprocess
from glob import glob

import nibabel as nb
import numpy as np


def prepare_images(bold_file, out_file, norf_file=None):
    """Concatenate BOLD and noRF images and save them out for NORDIC."""
    bold_img = nb.load(bold_file)
    bold_data = bold_img.get_fdata()  # get_fdata scales the data automatically

    n_noise_volumes = 0
    if norf_file:
        norf_img = nb.load(norf_file)

        # concatenate data
        norf_data = norf_img.get_fdata()
        bold_data = np.concatenate((bold_data, norf_data), axis=3)
        n_noise_volumes = norf_data.shape[3]

    # set slope and intercept in BOLD image header so no scaling is applied
    bold_img.header.set_slope_inter(1, 0)

    # set data type to float32 since there's no scaling to uint16 anymore
    bold_img.header.set_data_dtype(np.float32)

    # create a new image with the concatenated data
    concat_img = nb.Nifti1Image(bold_data, bold_img.affine, bold_img.header)

    # save it out for NORDIC
    # (the file will end up much bigger because there's no clean to-uint16 scaling)
    concat_img.to_filename(out_file)

    return n_noise_volumes


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


def run_nordic(mag_file, temp_dir):
    """Run NORDIC on the files to process."""
    print(f"Processing {os.path.basename(mag_file)}")
    out_dir = os.path.dirname(mag_file)
    basename = os.path.basename(mag_file)

    phase_file = None
    if "part-mag" in basename:
        is_complex = True
        mag_norf_file = mag_file.replace("_bold.nii.gz", "_noRF.nii.gz")
        if not os.path.isfile(mag_norf_file):
            mag_norf_file = None

        mag_filename = os.path.basename(mag_file)
        concat_mag_file = os.path.join(temp_dir, mag_filename)
        # rec entity comes before dir entity
        mag_fileparts = mag_filename.split("_")
        idx = [i for i, p in enumerate(mag_fileparts) if p.startswith("dir-")][0]
        # insert rec entity before dir entity
        mag_fileparts.insert(idx, "rec-nordic")
        out_mag_filename = "_".join(mag_fileparts)
        concat_mag_file = os.path.join(temp_dir, out_mag_filename)

        out_nordic_mag_file = os.path.join(out_dir, out_mag_filename)
        n_noise_volumes_mag = prepare_images(
            bold_file=mag_file,
            out_file=concat_mag_file,
            norf_file=mag_norf_file,
        )
        assert os.path.isfile(concat_mag_file), f"Failed to create {concat_mag_file}"

        phase_file = mag_file.replace("part-mag", "part-phase")
        phase_norf_file = phase_file.replace("_bold.nii.gz", "_noRF.nii.gz")
        if not os.path.isfile(phase_norf_file):
            phase_norf_file = None

        concat_phase_file = os.path.join(temp_dir, os.path.basename(phase_file))
        out_nordic_phase_file = out_nordic_mag_file.replace("part-mag", "part-phase")
        n_noise_volumes_phase = prepare_images(
            bold_file=phase_file,
            out_file=concat_phase_file,
            norf_file=phase_norf_file,
        )
        assert os.path.isfile(concat_phase_file)
        if n_noise_volumes_mag != n_noise_volumes_phase:
            raise ValueError(
                f"Number of noise volumes in {os.path.basename(mag_file)} and "
                f"{os.path.basename(phase_file)} do not match",
            )

    else:
        is_complex = False
        concat_mag_file = os.path.join(temp_dir, os.path.basename(mag_file))

        # rec entity comes before dir entity
        mag_fileparts = mag_filename.split("_")
        idx = [i for i, p in enumerate(mag_fileparts) if p.startswith("dir-")][0]
        # insert rec entity before dir entity
        mag_fileparts.insert(idx, "rec-nordic")
        out_mag_filename = "_".join(mag_fileparts)
        out_nordic_mag_file = os.path.join(out_dir, out_mag_filename)

        n_noise_volumes_mag = prepare_images(
            bold_file=mag_file,
            out_file=concat_mag_file,
            norf_file=None,
        )
        assert os.path.isfile(concat_mag_file)

    nordic_template = os.path.join(code_dir, "curation", "17_run_nordic.m")
    with open(nordic_template, "r") as fo:
        base_nordic_script = fo.read()

    # Modify, write out, and run the MATLAB script
    out_prefix = os.path.basename(mag_file).split("_bold.")[0]
    modified_nordic_script = (
        base_nordic_script.replace("{{ n_noise_vols }}", str(n_noise_volumes_mag))
        .replace("{{ mag_file }}", concat_mag_file)
        .replace("{{ out_prefix }}", out_prefix)
        .replace("{{ out_dir }}", temp_dir + "/")
    )

    if is_complex:
        modified_nordic_script = (
            modified_nordic_script.replace("{{ phase_file }}", concat_phase_file)
            .replace("{{ magnitude_only }}", "0")
            .replace("{{ make_complex_nii }}", "1")
        )
    else:
        modified_nordic_script = (
            modified_nordic_script.replace("{{ phase_file }}", "dummy.nii")
            .replace("{{ magnitude_only }}", "1")
            .replace("{{ make_complex_nii }}", "0")
        )

    out_nordic_script = os.path.join(
        temp_dir,
        out_prefix.replace("-", "").replace("_", "") + ".m",
    )
    print(f"Writing out MATLAB script to {out_nordic_script}")
    with open(out_nordic_script, "w") as fo:
        fo.write(modified_nordic_script)

    subprocess.run(
        [
            "matlab",
            "-nodisplay",
            "-nosplash",
            "-nodesktop",
            "-r",
            f"run('{out_nordic_script}');",
            "exit;",
        ],
    )

    # Find the outputs from the MATLAB script
    nordic_mag_file = os.path.join(temp_dir, out_prefix + "magn.nii")
    assert os.path.isfile(nordic_mag_file), f"Failed to create {nordic_mag_file}"

    # Split the data. We don't care about scaling at this point.
    nordic_mag_img = nb.load(nordic_mag_file)
    nordic_mag_img = nordic_mag_img.slicer[..., :-n_noise_volumes_mag]
    nordic_mag_img.to_filename(out_nordic_mag_file)

    if is_complex:
        nordic_phase_file = os.path.join(temp_dir, out_prefix + "phase.nii")
        assert os.path.isfile(nordic_phase_file), f"Failed to create {nordic_phase_file}"

        # Split the data. We don't care about scaling at this point.
        nordic_phase_img = nb.load(nordic_phase_file)
        nordic_phase_img = nordic_phase_img.slicer[..., :-n_noise_volumes_mag]
        nordic_phase_img.to_filename(out_nordic_phase_file)


if __name__ == "__main__":
    import sys

    code_dir = "/cbica/projects/pafin/code"
    in_dir = "/cbica/projects/pafin/dset"
    temp_dir = "/cbica/comp_space/pafin/NORDIC"
    os.makedirs(temp_dir, exist_ok=True)

    row_number = int(sys.argv[1])
    with open("files_to_nordic.txt", "r") as fo:
        mag_file = fo.readlines()[row_number].strip()

    run_nordic(mag_file, temp_dir)
