"""Plot median frame displacement (FD) across subjects."""

import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/fmriprep"
    data_dir = "/cbica/projects/pafin/code/data"
    figure_dir = "/cbica/projects/pafin/code/figures"

    # Get all subject directories
    in_files = glob(
        os.path.join(
            in_dir,
            "sub-*",
            "ses-*",
            "func",
            "*_desc-confounds_timeseries.tsv",
        )
    )
    in_files = [f for f in in_files if "rec-nordic" not in f]
    in_files = [f for f in in_files if "sub-PILOT" not in f]

    out_dfs = []
    for in_file in in_files:
        df = pd.read_table(in_file)
        # Drop non-steady-state volumes
        nss_cols = [col for col in df.columns if col.startswith("non_steady_state_outlier")]
        dummy_scans = 0
        if nss_cols:
            initial_volumes_df = df[nss_cols]
            dummy_scans = np.any(initial_volumes_df.to_numpy(), axis=1)
            dummy_scans = np.where(dummy_scans)[0]

            # reasonably assumes all NSS volumes are contiguous
            dummy_scans = int(dummy_scans[-1] + 1)

        df = df.iloc[dummy_scans:]
        fd = df["framewise_displacement"].median()
        entities = os.path.basename(in_file).split("_")
        task = [e for e in entities if e.startswith("task-")]
        task = task[0].replace("task-", "")
        subject = [e for e in entities if e.startswith("sub-")]
        subject = subject[0].replace("sub-", "")
        print(f"{subject} {task}: {fd}")

        # Add to output DataFrame
        out_df = pd.Series(
            {
                "subject": subject,
                "task": task,
                "fd": fd,
            }
        )
        out_dfs.append(out_df)

    out_df = pd.DataFrame(out_dfs)
    out_df.to_csv(os.path.join(data_dir, "median_fd.tsv"), sep="\t", index=False)

    # Plot median FD across subjects as a histogram, with hue by task
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(x="fd", data=out_df, hue="task", ax=ax)
    ax.set_title("Median Framewise Displacement (FD)")
    ax.set_xlabel("Task")
    ax.set_ylabel("FD")
    plt.savefig(os.path.join(figure_dir, "median_fd.png"))
