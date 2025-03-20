from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_matrix(corr_mat, network_labels, ax):
    """Plot matrix in subplot Axes."""
    assert corr_mat.shape[0] == len(network_labels)
    assert corr_mat.shape[1] == len(network_labels)

    # Determine order of nodes while retaining original order of networks
    unique_labels = []
    for label in network_labels:
        if label not in unique_labels:
            unique_labels.append(label)

    mapper = {label: f"{i:03d}_{label}" for i, label in enumerate(unique_labels)}
    mapped_network_labels = [mapper[label] for label in network_labels]
    community_order = np.argsort(mapped_network_labels)

    # Sort parcels by community
    corr_mat = corr_mat[community_order, :]
    corr_mat = corr_mat[:, community_order]

    # Get the community name associated with each network
    labels = np.array(network_labels)[community_order]
    unique_labels = sorted(set(labels))
    unique_labels = []
    for label in labels:
        if label not in unique_labels:
            unique_labels.append(label)

    # Find the locations for the community-separating lines
    break_idx = [0]
    end_idx = None
    for label in unique_labels:
        start_idx = np.where(labels == label)[0][0]
        if end_idx:
            break_idx.append(np.nanmean([start_idx, end_idx]))

        end_idx = np.where(labels == label)[0][-1]

    break_idx.append(len(labels))
    break_idx = np.array(break_idx)

    # Find the locations for the labels in the middles of the communities
    label_idx = np.nanmean(np.vstack((break_idx[1:], break_idx[:-1])), axis=0)

    np.fill_diagonal(corr_mat, 0)

    # Plot the correlation matrix
    im = ax.imshow(corr_mat, vmin=-1, vmax=1, cmap="seismic")

    # Add lines separating networks
    for idx in break_idx[1:-1]:
        ax.axes.axvline(idx, color="black")
        ax.axes.axhline(idx, color="black")

    # Add network names
    ax.axes.set_yticks(label_idx)
    ax.axes.set_xticks(label_idx)
    ax.axes.set_yticklabels(unique_labels)
    ax.axes.set_xticklabels(unique_labels, rotation=90)

    return im, ax


def plot_thing():
    for i_ax, atlas in enumerate(selected_atlases):
        i_row, i_col = divmod(i_ax, ncols)
        ax = fig.add_subplot(gs[i_row, i_col])
        atlas_idx = atlases.index(atlas)
        atlas_file = correlations_tsv[atlas_idx]
        dseg_file = atlas_tsvs[atlas_idx]

        column_name = COMMUNITY_LOOKUP.get(atlas, "network_label")
        dseg_df = pd.read_table(dseg_file)
        corrs_df = pd.read_table(atlas_file, index_col="Node")

        if atlas.startswith("4S"):
            atlas_mapper = {
                "CIT168Subcortical": "Subcortical",
                "ThalamusHCP": "Thalamus",
                "SubcorticalHCP": "Subcortical",
            }
            network_labels = dseg_df[column_name].fillna(dseg_df["atlas_name"]).tolist()
            network_labels = [atlas_mapper.get(network, network) for network in network_labels]
        elif column_name in dseg_df.columns:
            network_labels = dseg_df[column_name].fillna("None").tolist()
        else:
            network_labels = ["None"] * dseg_df.shape[0]

        im, ax = plot_matrix(
            corr_mat=corrs_df.to_numpy(),
            network_labels=network_labels,
            ax=ax,
        )
        ax.set_title(
            atlas,
            fontdict={"weight": "normal", "size": 20},
        )

    # Add colorbar in the reserved space
    cbar_ax = fig.add_subplot(gs[0, -1])
    plt.colorbar(im, cax=cbar_ax)
    cbar_ax.set_yticks([-1, 0, 1])
    fig.tight_layout()


if __name__ == "__main__":
    dseg_file = (
        "/cbica/projects/pafin/derivatives/xcp_d/atlases/atlas-4S156Parcels/"
        "atlas-4S156Parcels_dseg.tsv"
    )
    dseg_df = pd.read_table(dseg_file)

    atlas_mapper = {
        "CIT168Subcortical": "Subcortical",
        "ThalamusHCP": "Thalamus",
        "SubcorticalHCP": "Subcortical",
    }
    network_labels = dseg_df["network_label"].fillna(dseg_df["atlas_name"]).tolist()
    network_labels = [atlas_mapper.get(network, network) for network in network_labels]

    # Determine order of nodes while retaining original order of networks
    unique_labels = []
    for label in network_labels:
        if label not in unique_labels:
            unique_labels.append(label)

    mapper = {label: f"{i:03d}_{label}" for i, label in enumerate(unique_labels)}
    mapped_network_labels = [mapper[label] for label in network_labels]
    community_order = np.argsort(mapped_network_labels)

    # Get the community name associated with each network
    labels = np.array(network_labels)[community_order]
    unique_labels = sorted(set(labels))
    unique_labels = []
    for label in labels:
        if label not in unique_labels:
            unique_labels.append(label)

    # Find the locations for the community-separating lines
    break_idx = [0]
    end_idx = None
    for label in unique_labels:
        start_idx = np.where(labels == label)[0][0]
        if end_idx:
            break_idx.append(np.nanmean([start_idx, end_idx]))

        end_idx = np.where(labels == label)[0][-1]

    break_idx.append(len(labels))
    break_idx = np.array(break_idx)

    # Find the locations for the labels in the middles of the communities
    label_idx = np.nanmean(np.vstack((break_idx[1:], break_idx[:-1])), axis=0)

    corrmats = sorted(
        glob("/cbica/projects/pafin/derivatives/xcp_d/sub-*/ses-1/func/*seg-4S156Parcels*.tsv")
    )
    for task in ["bao", "rat"]:
        for denoising in ["none", "nordic"]:
            selected_corrmats = [cm for cm in corrmats if f"task-{task}" in cm]
            if denoising == "nordic":
                selected_corrmats = [cm for cm in selected_corrmats if "rec-nordic" in cm]
            else:
                selected_corrmats = [cm for cm in selected_corrmats if "_rec-" not in cm]

            print(len(selected_corrmats))
            arrs = []
            for cm in selected_corrmats:
                arrs.append(pd.read_table(cm, index_col="Node").to_numpy())

            arr_3d = np.dstack(arrs)
            print(arr_3d.shape)

            arr_3d_z = np.arctanh(arr_3d)

            # First mean
            mean_arr_z = np.nanmean(arr_3d_z, axis=2)
            mean_arr_r = np.tanh(mean_arr_z)

            # Sort parcels by community
            mean_arr_z = mean_arr_z[community_order, :]
            mean_arr_z = mean_arr_z[:, community_order]
            np.fill_diagonal(mean_arr_z, 0)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(mean_arr_r, cmap="seismic", vmin=-1, vmax=1)

            # Add lines separating networks
            for idx in break_idx[1:-1]:
                ax.axes.axvline(idx, color="black")
                ax.axes.axhline(idx, color="black")

            # Add network names
            ax.axes.set_yticks(label_idx)
            ax.axes.set_xticks(label_idx)
            ax.axes.set_yticklabels(unique_labels)
            ax.axes.set_xticklabels(unique_labels, rotation=90)

            fig.savefig(f"../figures/XCPD_task-{task}_denoising-{denoising}_Mean.png")
            plt.close()

            # Now standard deviation
            sd_arr_z = np.nanstd(arr_3d_z, axis=2)
            sd_arr_r = np.tanh(sd_arr_z)

            # Sort parcels by community
            sd_arr_z = sd_arr_z[community_order, :]
            sd_arr_z = sd_arr_z[:, community_order]

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(sd_arr_r, cmap="seismic", vmin=0)

            # Add lines separating networks
            for idx in break_idx[1:-1]:
                ax.axes.axvline(idx, color="black")
                ax.axes.axhline(idx, color="black")

            # Add network names
            ax.axes.set_yticks(label_idx)
            ax.axes.set_xticks(label_idx)
            ax.axes.set_yticklabels(unique_labels)
            ax.axes.set_xticklabels(unique_labels, rotation=90)

            fig.savefig(f"../figures/XCPD_task-{task}_denoising-{denoising}_StandardDeviation.png")
            plt.close()
