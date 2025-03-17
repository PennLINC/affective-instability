"""Plot T2* maps from tedana."""

import os
from glob import glob

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import templateflow.api as tflow
from nilearn import image, maskers, plotting


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/fmriprep"
    out_dir = "../figures"
    template = tflow.get("MNI152NLin6Asym", resolution="02", desc="brain", suffix="T1w", extension="nii.gz")
    mask = tflow.get("MNI152NLin6Asym", resolution="02", desc="brain", suffix="mask", extension="nii.gz")

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

        masker = maskers.NiftiMasker(mask, resampling_target="data")
        mean_img = image.mean_img(scalar_imgs, copy_header=True)
        mean_img = masker.inverse_transform(masker.fit_transform(mean_img))
        sd_img = image.math_img("np.std(img, axis=3)", img=scalar_imgs)
        sd_img = masker.inverse_transform(masker.transform(sd_img))

        # Plot mean and SD
        fig, axs = plt.subplots(2, 1, figsize=(10, 5))
        vmax0 = np.percentile(mean_img.get_fdata(), 98)
        vmax0 = np.round(vmax0)
        plotting.plot_stat_map(
            mean_img,
            bg_img=template,
            display_mode="z",
            cut_coords=[-30, -15, 0, 15, 30, 45, 60],
            axes=axs[0],
            figure=fig,
            symmetric_cbar=False,
            vmin=0,
            vmax=vmax0,
            cmap="viridis",
            annotate=False,
            black_bg=False,
            resampling_interpolation="nearest",
            colorbar=False,
        )
        vmax1 = np.percentile(sd_img.get_fdata(), 98)
        vmax1 = np.round(vmax1)
        plotting.plot_stat_map(
            sd_img,
            bg_img=template,
            display_mode="z",
            cut_coords=[-30, -15, 0, 15, 30, 45, 60],
            axes=axs[1],
            figure=fig,
            symmetric_cbar=False,
            vmin=0,
            vmax=vmax1,
            cmap="viridis",
            annotate=False,
            black_bg=False,
            resampling_interpolation="nearest",
            colorbar=False,
        )
        # fig.suptitle(title)
        fig.savefig(
            os.path.join(out_dir, f"{title.replace(' ', '_')}.png"),
            bbox_inches="tight",
        )
        plt.close()

        # Plot the colorbars
        fig, axs = plt.subplots(2, 1, figsize=(10, 0.5), layout='constrained')
        cmap = mpl.cm.viridis

        norm = mpl.colors.Normalize(vmin=0, vmax=vmax0)
        cbar = fig.colorbar(
            mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
            cax=axs[0],
            orientation='horizontal',
        )
        cbar.set_ticks([0, np.mean([0, vmax0]), vmax0])

        norm = mpl.colors.Normalize(vmin=0, vmax=vmax1)
        cbar = fig.colorbar(
            mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
            cax=axs[1],
            orientation='horizontal',
        )
        cbar.set_ticks([0, np.mean([0, vmax1]), vmax1])

        fig.savefig(
            os.path.join(out_dir, f"{title.replace(' ', '_')}_colorbar.png"),
            bbox_inches="tight",
        )
        plt.close()
