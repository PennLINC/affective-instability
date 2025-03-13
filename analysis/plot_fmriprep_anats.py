"""Plot T2* maps from tedana."""

from glob import glob

import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
from neuromaps.datasets import fetch_fslr
from surfplot import Plot


def surf_data_from_cifti(data, axis, surf_name):
    """From https://neurostars.org/t/separate-cifti-by-structure-in-python/17301/2.

    https://nbviewer.org/github/neurohackademy/nh2020-curriculum/blob/master/\
    we-nibabel-markiewicz/NiBabel.ipynb
    """
    assert isinstance(axis, (nb.cifti2.BrainModelAxis, nb.cifti2.ParcelsAxis))
    if isinstance(axis, nb.cifti2.BrainModelAxis):
        for name, data_indices, model in axis.iter_structures():
            # Iterates over volumetric and surface structures
            if name == surf_name:  # Just looking for a surface
                data = data.T[data_indices]
                # Assume brainmodels axis is last, move it to front
                vtx_indices = model.vertex
                # Generally 1-N, except medial wall vertices
                surf_data = np.zeros((vtx_indices.max() + 1,) + data.shape[1:], dtype=data.dtype)
                surf_data[vtx_indices] = data
                return surf_data
    else:
        if surf_name not in axis.nvertices:
            raise ValueError(
                f"No structure named {surf_name}.\n\n"
                f"Available structures are {list(axis.name.keys())}"
            )
        nvertices = axis.nvertices[surf_name]
        surf_data = np.zeros(nvertices)
        for i_label in range(len(axis.name)):
            element_dict = axis.get_element(i_label)[2]
            if surf_name in element_dict:
                element_idx = element_dict[surf_name]
                surf_data[element_idx] = data[0, i_label]

        return surf_data

    raise ValueError(f"No structure named {surf_name}")


def plot_surface(name, measure, files):
    surfaces = fetch_fslr()
    lh, rh = surfaces["midthickness"]

    imgs = [nb.load(f) for f in files]
    data = [img.get_fdata() for img in imgs]
    data = np.vstack(data)
    if measure == "Mean":
        data = np.mean(data, axis=0)
    else:
        data = np.std(data, axis=0)

    img_axes = [imgs[0].header.get_axis(i) for i in range(imgs[0].ndim)]
    lh_data = surf_data_from_cifti(
        data,
        img_axes[1],
        "CIFTI_STRUCTURE_CORTEX_LEFT",
    )
    rh_data = surf_data_from_cifti(
        data,
        img_axes[1],
        "CIFTI_STRUCTURE_CORTEX_RIGHT",
    )

    p = Plot(lh, rh, size=(800, 200), zoom=1.2, layout="row", mirror_views=True)
    p.add_layer(
        {"left": np.squeeze(lh_data), "right": np.squeeze(rh_data)},
        cmap="YlOrRd_r",
    )
    fig = p.build()
    fig.suptitle(measure, fontsize=24)
    fig.savefig(
        f"../figures/{name.replace(' ', '')}_{measure.lower().replace(' ', '')}.png",
        bbox_inches="tight",
    )
    plt.close()


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/fmriprep"

    patterns = {
        "Cortical Thickness": "sub-*/ses-1/anat/*_space-fsLR_den-91k_thickness.dscalar.nii",
        "Sulcal Curvature": "sub-*/ses-1/anat/*_space-fsLR_den-91k_curv.dscalar.nii",
        "Sulcal Depth": "sub-*/ses-1/anat/*_space-fsLR_den-91k_sulc.dscalar.nii",
    }
    for name, pattern in patterns.items():
        files = sorted(glob(pattern))
        for measure in ["Mean", "Standard Deviation"]:
            plot_surface(name, measure, files)
