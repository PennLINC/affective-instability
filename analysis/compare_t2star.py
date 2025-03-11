import json
import os
from glob import glob

import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D
from nilearn import image, masking, plotting


def get_tes(files):
    echo_times = []
    for f in files:
        json_file = f.replace(".nii.gz", ".json")
        with open(json_file, "r") as fo:
            metadata = json.load(fo)
            te = metadata["EchoTime"]
            echo_times.append(te * 1000)
    return echo_times


def mm2vox(xyz, affine):
    """Convert coordinates to matrix subscripts.

    .. versionchanged:: 0.0.8

        * [ENH] This function was part of `nimare.transforms` in previous versions (0.0.3-0.0.7)

    Parameters
    ----------
    xyz : (X, 3) :obj:`numpy.ndarray`
        Coordinates in image-space.
        One row for each coordinate, with three columns: x, y, and z.
    affine : (4, 4) :obj:`numpy.ndarray`
        Affine matrix from image.

    Returns
    -------
    ijk : (X, 3) :obj:`numpy.ndarray`
        Matrix subscripts for coordinates being transformed.

    Notes
    -----
    From here:
    http://blog.chrisgorgolewski.org/2014/12/how-to-convert-between-voxel-and-mm.html
    """
    ijk = nb.affines.apply_affine(np.linalg.inv(affine), xyz).astype(int)
    return ijk


def collect_t2star_results(in_dir):
    """Collect and compare masked T2* maps."""
    nordic_masks = sorted(
        glob(
            os.path.join(
                in_dir,
                "derivatives/fmriprep/sub-*/ses-1/func/",
                "*_rec-nordic_*_part-mag_space-T1w_desc-brain_mask.nii.gz",
            ),
        ),
    )
    rows = []
    for nordic_mask in nordic_masks:
        run_dir = os.path.dirname(nordic_mask)
        fname = os.path.basename(nordic_mask)
        print(fname)
        fileparts = fname.split("_")
        fileparts = [p for p in fileparts if "part" not in p]
        fileparts = [p for p in fileparts if "desc" not in p]

        nonordic_mask = nordic_mask.replace("rec-nordic_", "")

        nordic_t2smap = fname.replace(
            "part-mag_space-T1w_desc-brain_mask.nii.gz",
            "space-T1w_T2starmap.nii.gz",
        )
        # Drop dir-<AP|PA>
        t2smap_fileparts = [p for p in nordic_t2smap.split("_") if "dir" not in p]
        nordic_t2smap = "_".join(t2smap_fileparts)

        nonordic_t2smap = nonordic_mask.replace(
            "part-mag_space-T1w_desc-brain_mask.nii.gz",
            "space-T1w_T2starmap.nii.gz",
        )
        t2smap_fileparts = [p for p in nonordic_t2smap.split("_") if "dir" not in p]
        nonordic_t2smap = "_".join(t2smap_fileparts)

        nordic_t2smap = os.path.join(run_dir, nordic_t2smap)
        nonordic_mask = os.path.join(run_dir, nonordic_mask)
        nonordic_t2smap = os.path.join(run_dir, nonordic_t2smap)

        assert os.path.isfile(nordic_mask), nordic_mask
        assert os.path.isfile(nordic_t2smap), nordic_t2smap
        assert os.path.isfile(nonordic_mask), nonordic_mask
        assert os.path.isfile(nonordic_t2smap), nonordic_t2smap

        nordic_t2_arr = masking.apply_mask(nordic_t2smap, nonordic_mask)
        nonordic_t2_arr = masking.apply_mask(nonordic_t2smap, nonordic_mask)

        corr = np.corrcoef(nordic_t2_arr, nonordic_t2_arr)[0, 1]
        row = (
            [fname]
            + [f.split("-")[1] for f in fileparts]
            + [corr, nordic_t2_arr.mean(), nonordic_t2_arr.mean()]
        )
        rows.append(row)

    columns = (
        ["fname"]
        + [f.split("-")[0] for f in fileparts]
        + ["pearson_correlation", "nordic_t2_mean", "nonordic_t2_mean"]
    )
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv("../data/t2star_nordic_comparison.tsv", sep="\t", index=False)


def plot_echo_wise_values(in_dir):
    """Plot echo-wise values for a single voxel."""
    colors = ["lightblue", "orange", "blue", "red"]

    # Plot echo-wise values for a single voxel
    echowise_queries = {
        "Raw": "dset/sub-*/ses-1/func/*_echo-1_part-mag_bold.nii.gz",
        "Raw NORDIC": "dset/sub-*/ses-1/func/*_rec-nordic_*_echo-1_part-mag_bold.nii.gz",
        "fMRIPrep": (
            "derivatives/fmriprep/sub-*/ses-1/func/*_echo-1_part-mag_desc-preproc_bold.nii.gz"
        ),
        "fMRIPrep NORDIC": (
            "derivatives/fmriprep/sub-*/ses-1/func/"
            "*_rec-nordic_*_echo-1_part-mag_desc-preproc_bold.nii.gz"
        ),
    }

    image_groups = {}
    for name, pattern in echowise_queries.items():
        files_found = sorted(glob(pattern))
        imgs = [nb.load(f) for f in files_found]
        if name == "Raw":
            echo_times = get_tes(files_found)
            n_echoes = len(echo_times)
            n_trs = imgs[0].shape[3]

        assert len(imgs) == n_echoes

        print(imgs[0].shape)
        image_groups[name] = imgs

    x, y, z = 50, -5, 30
    # x, y, z = -50, -20, 35
    for name, imgs in image_groups.items():
        print(name)
        mean_img = image.mean_img(imgs[1])
        plotting.plot_epi(mean_img, cut_coords=[x, y, z], title=name)
        ijk = mm2vox([x, y, z], mean_img.affine)
        print(ijk)

    i, j, k = ijk

    timeseries_groups = {}
    for name, imgs in image_groups.items():
        timeseries = np.zeros((n_echoes, n_trs))

        for i_echo in range(n_echoes):
            data = imgs[i_echo].get_fdata()
            timeseries[i_echo, :] = data[i, j, k, :]

        timeseries_groups[name] = timeseries

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(14, 6))

    color_names = {}
    for i_name, (name, timeseries) in enumerate(timeseries_groups.items()):
        color = colors[i_name]
        color_names[name] = color
        for j_echo in range(n_echoes):
            rep_echo_times = np.ones(n_trs) * echo_times[j_echo]
            ax.scatter(
                rep_echo_times + i_name,
                timeseries[j_echo, :],
                alpha=0.05,
                color=color,
            )

    legend_elements = []
    for k, v in color_names.items():
        line = Line2D([0], [0], marker="o", color="w", markerfacecolor=v, label=k, markersize=10)
        legend_elements.append(line)

    ax.legend(handles=legend_elements)
    ax.set_xlabel("Echo Time (ms)")
    ax.set_ylabel("BOLD signal")
    fig.savefig("effect_of_nordic.png")


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin"
    collect_t2star_results(in_dir)
