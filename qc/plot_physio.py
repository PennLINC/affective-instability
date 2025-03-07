"""Loop over all subjects and tasks and plot the cardiac and respiratory signals."""

import json
import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_physio(cardiac_files, subject):
    """Plot the cardiac and respiratory signals.

    Parameters
    ----------
    cardiac_files : list
        List of paths to the cardiac physiological files.
    subject : str
        Subject ID.
    """
    sns.set_style("whitegrid")

    fig, axes = plt.subplots(figsize=(16, 16), nrows=len(cardiac_files), sharex=True)

    min_time, max_time = 0, 0
    for i, cardiac_file in enumerate(cardiac_files):
        task = cardiac_file.split("task-")[1].split("_")[0]
        respiratory_file = cardiac_file.replace("cardiac_", "respiratory_")
        cardiac_json = cardiac_file.replace(".tsv.gz", ".json")
        respiratory_json = respiratory_file.replace(".tsv.gz", ".json")

        cardiac_data = np.loadtxt(cardiac_file)
        respiratory_data = np.loadtxt(respiratory_file)

        with open(cardiac_json, "r") as fo:
            cardiac_metadata = json.load(fo)

        with open(respiratory_json, "r") as fo:
            respiratory_metadata = json.load(fo)

        cardiac_fs = cardiac_metadata["SamplingFrequency"]
        respiratory_fs = respiratory_metadata["SamplingFrequency"]
        title = f"Subject {subject} Task {task}"
        print(title)
        cardiac_time = (np.arange(0, cardiac_data.size) / cardiac_fs) + cardiac_metadata[
            "StartTime"
        ]
        cardiac_data = (cardiac_data - np.nanmean(cardiac_data)) / np.nanstd(cardiac_data)
        axes[i].plot(cardiac_time, cardiac_data - 5, label="cardiac")
        max_time = max(max(cardiac_time), max_time)
        min_time = min(min(cardiac_time), min_time)

        respiratory_time = (
            np.arange(0, respiratory_data.size) / respiratory_fs
        ) + respiratory_metadata["StartTime"]
        respiratory_data = (respiratory_data - np.nanmean(respiratory_data)) / np.nanstd(
            respiratory_data
        )
        axes[i].plot(respiratory_time, respiratory_data + 5, label="respiratory")
        axes[i].axvline(0, label="scan start", color="black")

        max_time = max(max(respiratory_time), max_time)
        min_time = min(min(respiratory_time), min_time)
        axes[i].legend()
        axes[i].set_title(title, fontsize=30)

    axes[i].set_xlim(min_time, max_time)
    axes[i].set_xlabel("Time (s)")

    fig.tight_layout()
    fig.savefig(f"../figures/{subject}_physio.png")


if __name__ == "__main__":
    dset_dir = "/cbica/projects/pafin/dset"
    subjects = sorted(glob(os.path.join(dset_dir, "sub-*")))
    subjects = [os.path.basename(subject) for subject in subjects]
    for subject in subjects:
        cardiac_files = sorted(
            glob(
                os.path.join(
                    dset_dir, subject, "ses-*", "func", "*_recording-cardiac_physio.tsv.gz"
                )
            )
        )
        if not cardiac_files:
            print(f"No physio for {subject}")
            continue
        plot_physio(cardiac_files, subject)
