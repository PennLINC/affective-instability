"""Plot scalar maps from QSIRecon."""

import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
from nilearn import image, plotting


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/qsirecon/derivatives"
    out_dir = "../figures"

    patterns = {
        "DSIStudio GQI FA": "qsirecon-DSIStudioGQI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-tensor_param-fa_dwimap.nii.gz",
        "DSIStudio GQI MD": "qsirecon-DSIStudioGQI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-tensor_param-md_dwimap.nii.gz",
        "DSIStudio GQI GFA": "qsirecon-DSIStudioGQI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-gqi_param-gfa_dwimap.nii.gz",
    }
    for title, pattern in patterns.items():
        # Get all scalar maps
        scalar_maps = sorted(glob(os.path.join(in_dir, pattern)))
        scalar_maps = [f for f in scalar_maps if "PILOT" not in f]
        print(f"{title}: {len(scalar_maps)}")

        mean_img = image.mean_img(scalar_maps, copy_header=True)
        sd_img = image.math_img("np.std(img, axis=3)", img=scalar_maps)

        # Plot mean and SD
        fig, axs = plt.subplots(2, 1, figsize=(10, 5))
        vmax = np.percentile(mean_img.get_fdata(), 95)
        plotting.plot_stat_map(
            mean_img,
            display_mode="z",
            cut_coords=[-30, -15, 0, 15, 30, 45, 60],
            axes=axs[0],
            figure=fig,
            symmetric_cbar=False,
            vmin=0,
            vmax=vmax,
            cmap="viridis",
            annotate=False,
        )
        vmax = np.percentile(sd_img.get_fdata(), 95)
        plotting.plot_stat_map(
            sd_img,
            display_mode="z",
            cut_coords=[-30, -15, 0, 15, 30, 45, 60],
            axes=axs[1],
            figure=fig,
            symmetric_cbar=False,
            vmin=0,
            vmax=vmax,
            cmap="viridis",
            annotate=False,
        )
        fig.suptitle(title)
        fig.savefig(os.path.join(out_dir, f"{title.replace(' ', '_')}.png"), bbox_inches="tight")
        plt.close()
