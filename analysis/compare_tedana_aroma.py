"""Compare the results of TEDANA and AROMA."""

import os
from glob import glob

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/derivatives/tedana+aroma"
    out_dir = "../figures"

    files = sorted(
        glob(
            os.path.join(
                in_dir,
                "sub-*",
                "ses-1",
                "func",
                "*_desc-tedana+aroma_metrics.tsv",
            )
        )
    )
    file_dicts = []
    for file in files:
        df = pd.read_table(file)
        subject = os.path.basename(file).split("_")[0]
        file_dict = {
            "file": os.path.basename(file),
            "subject": subject,
            "denoising": "NORDIC" if "nordic" in os.path.basename(file) else "None",
            "n_components": df.shape[0],
            "n_accepted": df[df["classification"] == "accepted"].shape[0],
            "varex_accepted": df[df["classification"] == "accepted"][
                "total_variance_explained"
            ].sum(),
            "varex_unmodeled": 1 - df["total_variance_explained"].sum(),
        }

        rejected_df = df.loc[df["classification"] == "rejected"]
        rejected_both_df = rejected_df.loc[
            rejected_df["classification_tags"].str.contains("TEDANA")
            & rejected_df["classification_tags"].str.contains("AROMA")
        ]
        rejected_aroma_df = rejected_df.loc[
            rejected_df["classification_tags"].str.contains("AROMA")
            & ~rejected_df["classification_tags"].str.contains("TEDANA")
        ]
        rejected_tedana_df = rejected_df.loc[
            ~rejected_df["classification_tags"].str.contains("AROMA")
            & rejected_df["classification_tags"].str.contains("TEDANA")
        ]

        file_dict["n_rejected_both"] = rejected_both_df.shape[0]
        file_dict["n_rejected_aroma"] = rejected_aroma_df.shape[0]
        file_dict["n_rejected_tedana"] = rejected_tedana_df.shape[0]
        file_dict["varex_rejected_both"] = rejected_both_df["total_variance_explained"].sum()
        file_dict["varex_rejected_aroma"] = rejected_aroma_df["total_variance_explained"].sum()
        file_dict["varex_rejected_tedana"] = rejected_tedana_df["total_variance_explained"].sum()

        file_dicts.append(file_dict)

    group_df = pd.DataFrame(file_dicts)
    group_df.to_csv("../data/AROMA+tedana_denoising_metrics.tsv", index=False, sep="\t")

    # Boxplot of variance explained, organized as "accepted", "rejected by AROMA",
    # "rejected by TEDANA", "rejected by both", "unmodeled" across runs
    df_varex = group_df.melt(
        id_vars=["subject", "denoising"],
        value_vars=[
            "varex_accepted",
            "varex_rejected_aroma",
            "varex_rejected_tedana",
            "varex_rejected_both",
            "varex_unmodeled",
        ],
        value_name="Variance Explained",
        var_name="Classification",
    )

    sns.set_theme(style="ticks")
    f, ax = plt.subplots(figsize=(7, 6))
    sns.boxenplot(
        df_varex,
        x="Variance Explained",
        y="Classification",
        hue="denoising",
        palette="vlag",
    )
    ax.xaxis.grid(True)
    ax.set_xlim(0, 1)
    ax.set(ylabel="")
    sns.despine(trim=True, left=True)
    f.tight_layout()
    f.savefig(os.path.join(out_dir, "AROMA+tedana_variance_explained.png"), bbox_inches="tight")
    plt.close()

    # Boxplot of number of components, organized as "accepted", "rejected by AROMA",
    # "rejected by TEDANA", "rejected by both" across runs
    df_ncomps = group_df.melt(
        id_vars=["subject", "denoising"],
        value_vars=[
            "n_accepted",
            "n_rejected_aroma",
            "n_rejected_tedana",
            "n_rejected_both",
        ],
        value_name="Number of Components",
        var_name="Classification",
    )

    sns.set_theme(style="ticks")
    f, ax = plt.subplots(figsize=(7, 6))
    sns.boxenplot(
        df_ncomps,
        x="Number of Components",
        y="Classification",
        hue="denoising",
        palette="vlag",
    )
    ax.xaxis.grid(True)
    ax.set_xlim(0, None)
    ax.set(ylabel="")
    sns.despine(trim=True, left=True)
    f.tight_layout()
    f.savefig(os.path.join(out_dir, "AROMA+tedana_n_components.png"), bbox_inches="tight")
    plt.close()
