"""Plot CBF maps from ASLPrep."""

import os
from glob import glob

import matplotlib.pyplot as plt
from nilearn import image, plotting


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/aslprep"
    out_dir = "../figures"

    patterns = {
        "ASLPrep CBF": "sub-*/ses-1/perf/*_space-MNI152NLin6Asym_cbf.nii.gz",
        "BASIL ATT": "sub-*/ses-1/perf/*_space-MNI152NLin6Asym_desc-basil_att.nii.gz",
        "BASIL CBF": "sub-*/ses-1/perf/*_space-MNI152NLin6Asym_desc-basil_cbf.nii.gz",
        "BASIL GM CBF": "sub-*/ses-1/perf/*_space-MNI152NLin6Asym_desc-basilGM_cbf.nii.gz",
        "BASIL WM CBF": "sub-*/ses-1/perf/*_space-MNI152NLin6Asym_desc-basilWM_cbf.nii.gz",
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
        plotting.plot_stat_map(
            mean_img,
            display_mode="z",
            cut_coords=[-30, -15, 0, 15, 30, 45, 60],
            title="Mean",
            axes=axs[0],
            figure=fig,
            symmetric_cbar=False,
            vmin=0,
            vmax=120,
            cmap="YlOrRd",
        )
        plotting.plot_stat_map(
            sd_img,
            display_mode="z",
            cut_coords=[-30, -15, 0, 15, 30, 45, 60],
            title="Standard Deviation",
            axes=axs[1],
            figure=fig,
            symmetric_cbar=False,
            vmin=0,
            cmap="YlOrRd",
        )
        fig.suptitle(title)
        fig.savefig(os.path.join(out_dir, f"{title.replace(' ', '_')}.png"), bbox_inches="tight")
        plt.close()
