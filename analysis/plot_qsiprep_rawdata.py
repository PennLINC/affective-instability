#!/usr/bin/env python

import shutil
import subprocess
from pathlib import Path

import ants
import imageio.v3 as iio
import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
from nilearn import image, plotting


def resample_processed_into_raw(processed_nifti, raw_nifti, temp_dir, image_index, subid, sesid):
    """Select a 3d volume from raw_nifti and transform the corresponding
    volume from processed_nifti so they can be plotted next to each other.

    Parameters
    ----------
    image_index : int
        The volume number to extract from the 4D datasets
    """
    # Load the reference image
    ref_img = ants.image_read(str(ref_img_path))

    # Load the image from image_index using nilearn, save as a single-volume nifti
    # No need to transform the processed image, it is already in ACPC space
    processed_vol_path = (
        temp_dir / f"{subid}_{sesid}_space-ACPC_desc-preproc_dwi_vol-{image_index}.nii"
    )
    processed_vol = image.index_img(str(processed_nifti), image_index)
    processed_vol.to_filename(processed_vol_path)

    # Transform the raw image at image_index to the ACPC space
    raw_nii = image.index_img(str(raw_nifti), image_index)
    raw_nii_path = temp_dir / f"{subid}_{sesid}_vol-{image_index}_raw.nii"
    raw_nii.to_filename(raw_nii_path)
    raw_ants = ants.image_read(str(raw_nii_path))
    raw_vol = ants.apply_transforms(
        fixed=ref_img,
        moving=raw_ants,
        transformlist=[str(raw_to_acpc_xfm)],
        interpolator="lanczosWindowedSinc",
    )
    resampled_raw_nii_path = temp_dir / f"{subid}_{sesid}_vol-{image_index}_space-ACPC_raw.nii"
    ants.image_write(raw_vol, str(resampled_raw_nii_path))

    temp_files_to_delete = [
        raw_nii_path,
    ]

    for file in temp_files_to_delete:
        Path(file).unlink()

    return resampled_raw_nii_path, processed_vol_path


def make_figure(
    out_dir,
    raw_nii_path,
    registered_nii_path,
    image_index,
    subid,
    sesid,
    crop_proportion=0.1,
):
    """Create a figure comparing raw and registered volumes.

    Parameters
    ----------
    raw_nii_path : str or Path
        Path to the raw nifti file
    registered_nii_path : str or Path
        Path to the registered nifti file
    image_index : int
        Volume number for labeling
    crop_proportion : float, optional
        Proportion of image edges to crop (default: 0.15 for 15%)
    """
    # Load the specific volumes
    raw_nii = image.load_img(raw_nii_path)
    registered_nii = image.load_img(registered_nii_path)

    slices_to_plot = {
        "x": [-10.0],
        "y": [-25.0],
        "z": [4.0],
    }

    # Calculate number of rows needed for the plots
    n_planes = len(slices_to_plot)

    # Create the figure
    fig, axes = plt.subplots(n_planes, 2, figsize=(15, 6.5 * n_planes))
    # Get the data range for this plane
    raw_data = raw_nii.get_fdata()
    reg_data = registered_nii.get_fdata()

    # Calculate 2nd and 98th percentiles from combined data, clipped at 0
    all_data = np.clip(np.concatenate([raw_data.ravel(), reg_data.ravel()]), 0, None)
    vmin = np.percentile(all_data, 0.5)
    vmax = np.percentile(all_data, 99.5)

    # Plot each plane
    for idx, (plane, coords) in enumerate(slices_to_plot.items()):
        # Plot raw volume
        plotting.plot_anat(
            raw_nii,
            display_mode=plane,
            cut_coords=coords,
            title="",
            axes=axes[idx, 0],
            draw_cross=False,
            annotate=False,
            vmin=vmin,
            vmax=vmax,
        )

        # Plot registered volume
        plotting.plot_anat(
            registered_nii,
            display_mode=plane,
            cut_coords=coords,
            title="",
            axes=axes[idx, 1],
            draw_cross=False,
            annotate=False,
            vmin=vmin,
            vmax=vmax,
        )

    # Remove all whitespace between subplots and at edges
    plt.subplots_adjust(hspace=0, wspace=0, left=0, right=1, bottom=0, top=1)

    # Save the figure
    fig_path = out_dir / f"QSIPrep_{subid}_{sesid}_vol-{image_index}_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Crop the saved figure
    img = iio.imread(fig_path)

    # Calculate crop dimensions based on the provided proportion
    h, w = img.shape[:2]
    crop_h = int(h * crop_proportion)
    crop_w = int(w * crop_proportion)

    # Crop the image
    cropped = img[crop_h:-crop_h, crop_w:-crop_w]

    # Save the cropped image
    iio.imwrite(fig_path, cropped)


if __name__ == "__main__":
    data_root = Path("/cbica/projects/pafin")
    out_dir = Path("/cbica/projects/pafin/code/figures")
    temp_dir = Path("/cbica/comp_space/pafin/qsiprep_figures")
    temp_dir.mkdir(parents=False, exist_ok=True)

    subjects = sorted((data_root / "dset").glob("sub-*"))
    subjects = ["sub-24683"]
    for subject in subjects:
        # subid = subject.name
        subid = subject
        sesids = sorted((data_root / "dset" / subid).glob("ses-*"))
        sesids = [sesid.name for sesid in sesids]
        for sesid in sesids:
            print(f"Processing {subid} {sesid}")

            # The dir-PA nifti is always the first
            raw_nifti = (
                data_root
                / "dset"
                / subid
                / sesid
                / "dwi"
                / f"{subid}_{sesid}_dir-AP_run-01_part-mag_dwi.nii.gz"
            )
            processed_nifti = (
                data_root
                / "derivatives"
                / "qsiprep"
                / subid
                / sesid
                / "dwi"
                / f"{subid}_{sesid}_dir-AP_space-ACPC_desc-preproc_dwi.nii.gz"
            )
            raw_to_acpc_xfm = (
                processed_nifti.parent.parent
                / "anat"
                / f"{subid}_{sesid}_from-raw_to-ACPC_rigid.mat"
            )
            raw_mean_path = temp_dir / f"{subid}_{sesid}_dir-AP_run-1_dwi_mean.nii"
            processed_mean_path = temp_dir / f"{subid}_{sesid}_space-ACPC_desc-preproc_dwi_mean.nii"

            # If there is not transform file, we need to run the registration
            if not Path(raw_to_acpc_xfm).exists():
                # Load the nifti files
                raw_img = nb.load(raw_nifti)
                processed_img = nb.load(processed_nifti)

                # Get the data and calculate mean of first 4 volumes
                raw_data = raw_img.get_fdata()
                processed_data = processed_img.get_fdata()

                raw_mean = raw_data[..., :4].mean(axis=3)
                processed_mean = processed_data[..., :4].mean(axis=3)

                # Create new nifti images with the mean data
                raw_mean_img = nb.Nifti1Image(raw_mean, raw_img.affine, raw_img.header)
                processed_mean_img = nb.Nifti1Image(
                    processed_mean,
                    processed_img.affine,
                    processed_img.header,
                )

                # Save the mean images
                nb.save(raw_mean_img, raw_mean_path)
                nb.save(processed_mean_img, processed_mean_path)

                # Load the mean images directly with ANTs
                raw_mean_ants = ants.image_read(str(raw_mean_path))
                processed_mean_ants = ants.image_read(str(processed_mean_path))

                # Perform rigid registration
                registration = ants.registration(
                    fixed=processed_mean_ants,
                    moving=raw_mean_ants,
                    type_of_transform="Similarity",
                )
                shutil.copy(registration["fwdtransforms"][0], raw_to_acpc_xfm)
                # Apply transform using lanczoswindowedsinc interpolation
                registered_processed = ants.apply_transforms(
                    fixed=processed_mean_ants,
                    moving=raw_mean_ants,
                    transformlist=registration["fwdtransforms"],
                    interpolator="lanczosWindowedSinc",
                )

                # Save the registered image
                registered_path = temp_dir / f"{subid}_{sesid}_space-ACPC_desc-preproc_dwi_mean.nii"
                ants.image_write(registered_processed, str(registered_path))

            # use nilearn image.crop_img to get the cropped reference image
            ref_img_path = temp_dir / f"{subid}_{sesid}_space-ACPC_desc-cropped_dwi.nii"
            if not Path(ref_img_path).exists():
                # Call 3dAutobox using subprocess
                cmd = [
                    "3dAutobox",
                    "-prefix",
                    str(ref_img_path),
                    "-input",
                    str(processed_mean_path),
                    "-npad",
                    "5",
                ]

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    raise RuntimeError(f"3dAutobox failed with error: {stderr.decode()}")

            # b = 5
            lowb_vols = [0, 1, 14, 27, 40, 53, 66, 79, 103]
            # b = 2590, 2595, 2600
            midb_vols = [7, 12, 56, 87, 97]
            # b = 5000
            highb_vols = [15, 22, 33, 44, 71, 86]
            vols_to_plot = lowb_vols + midb_vols + highb_vols
            for vol in vols_to_plot:
                print(f"Plotting volume {vol}")
                raw_nii_path, registered_nii_path = resample_processed_into_raw(
                    processed_nifti,
                    raw_nifti,
                    temp_dir,
                    vol,
                    subid,
                    sesid,
                )
                make_figure(out_dir, raw_nii_path, registered_nii_path, vol, subid, sesid)
