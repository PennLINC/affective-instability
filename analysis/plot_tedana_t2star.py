"""Plot T2* maps from tedana."""

import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import templateflow.api as tflow
from nilearn import image, plotting


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/fmriprep"
    out_dir = "../figures"
    template = tflow.get("MNI152NLin6Asym", resolution="02", desc=None, suffix="T1w", extension="nii.gz")

    patterns = {
        "T2star": "sub-*/ses-1/func/*_space-MNI152NLin6Asym_res-2_T2starmap.nii.gz",
    }
    for title, pattern in patterns.items():
        # Get all scalar maps
        scalar_maps = sorted(glob(os.path.join(in_dir, pattern)))
        scalar_maps = [f for f in scalar_maps if "PILOT" not in f]
        print(f"{title}: {len(scalar_maps)}")
        scalar_imgs = [image.math_img("img * 1000", img=img) for img in scalar_maps]

        mean_img = image.mean_img(scalar_imgs, copy_header=True)
        sd_img = image.math_img("np.std(img, axis=3)", img=scalar_imgs)

        # Plot mean and SD
        fig, axs = plt.subplots(2, 1, figsize=(10, 5))
        vmax = np.percentile(mean_img.get_fdata(), 98)
        plotting.plot_stat_map(
            mean_img,
            bg_img=template,
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
        vmax = np.percentile(sd_img.get_fdata(), 98)
        plotting.plot_stat_map(
            sd_img,
            bg_img=template,
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
        # fig.suptitle(title)
        fig.savefig(os.path.join(out_dir, f"{title.replace(' ', '_')}.png"), bbox_inches="tight")
        plt.close()
