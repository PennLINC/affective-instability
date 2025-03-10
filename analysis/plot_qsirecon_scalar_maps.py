"""Plot scalar maps from QSIRecon."""

import os
from glob import glob

import matplotlib.pyplot as plt
from nilearn import image, plotting


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/qsirecon/derivatives"
    out_dir = "../figures"

    patterns = {
        "NODDI ICVF": "qsirecon-wmNODDI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-noddi_param-icvf_dwimap.nii.gz",
        "TORTOISE RTOP": "qsirecon-TORTOISE_model-MAPMRI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-mapmri_param-rtop_dwimap.nii.gz",
        "DSIStudio GQI FA": "qsirecon-DSIStudioGQI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-tensor_param-fa_dwimap.nii.gz",
        "DSIStudio GQI MD": "qsirecon-DSIStudioGQI/sub-*/ses-1/dwi/*_space-MNI152NLin2009cAsym_model-tensor_param-md_dwimap.nii.gz",
    }
    for title, pattern in patterns.items():
        # Get all scalar maps
        scalar_maps = sorted(glob(os.path.join(in_dir, pattern)))
        print(f"{title}: {len(scalar_maps)}")

        mean_img = image.mean_img(scalar_maps)
        sd_img = image.math_img("np.std(img, axis=3)", img=scalar_maps)

        # Plot mean and SD
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        plotting.plot_stat_map(
            mean_img,
            display_mode="z",
            cut_coords=[-30, -20, -10, 0, 10, 20, 30, 40, 50, 60],
            axes=axs[0],
            figure=fig,
        )
        plotting.plot_stat_map(
            sd_img,
            display_mode="z",
            cut_coords=[-30, -20, -10, 0, 10, 20, 30, 40, 50, 60],
            axes=axs[1],
            figure=fig,
        )
        fig.suptitle(title)
        plt.savefig(os.path.join(out_dir, f"{title.replace(' ', '_')}.png"))
        plt.close()
