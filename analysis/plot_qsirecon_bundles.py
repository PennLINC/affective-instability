"""
============================
Visualizing AFQ derivatives
============================

Visualizing the results of a pyAFQ analysis is useful because it allows us to
inspect the results of the analysis and to communicate the results to others.
The pyAFQ pipeline produces a number of different kinds of outputs, including
visualizations that can be used for quality control and for quick examination
of the results of the analysis.

However, when communicating the results of pyAFQ analysis, it is often useful
to have more specific control over the visualization that is produced. In
addition, it is often useful to have visualizations that are visually appealing
and striking. In this tutorial, we will use the `fury <https://fury.gl/>`_
library [1]_ to visualize outputs of pyAFQ as publication-ready figures.

"""

import gzip
import shutil
from pathlib import Path

import nibabel as nb
import numpy as np
from AFQ.viz.utils import PanelFigure
from dipy.io.streamline import load_tck
from dipy.tracking.streamline import transform_streamlines
from fury import actor, window
from matplotlib.cm import tab20


def lines_as_tubes(sl, line_width, **kwargs):
    line_actor = actor.line(sl, **kwargs)
    line_actor.GetProperty().SetRenderLinesAsTubes(True)
    line_actor.GetProperty().SetLineWidth(line_width)
    return line_actor


def slice_volume(data, x=None, y=None, z=None):
    slicer_actors = []
    slicer_actor_z = actor.slicer(data)
    if z is not None:
        slicer_actor_z.display_extent(0, data.shape[0] - 1, 0, data.shape[1] - 1, z, z)
        slicer_actors.append(slicer_actor_z)
    if y is not None:
        slicer_actor_y = slicer_actor_z.copy()
        slicer_actor_y.display_extent(0, data.shape[0] - 1, y, y, 0, data.shape[2] - 1)
        slicer_actors.append(slicer_actor_y)
    if x is not None:
        slicer_actor_x = slicer_actor_z.copy()
        slicer_actor_x.display_extent(x, x, 0, data.shape[1] - 1, 0, data.shape[2] - 1)
        slicer_actors.append(slicer_actor_x)

    return slicer_actors


def get_bundle_data(data_root, subid, sesid, bundle_name, reference):
    bundle_path = (
        data_root
        / f"sub-{subid}"
        / f"ses-{sesid}"
        / "dwi"
        / f"sub-{subid}_ses-{sesid}_space-ACPC_model-gqi_bundle-{bundle_name}_streamlines.tck"
    )
    bundle_path_gz = bundle_path.with_suffix(".tck.gz")
    if bundle_path.exists():
        return load_tck(bundle_path, reference=reference)
    elif bundle_path_gz.exists():
        with gzip.open(bundle_path_gz, "rb") as f_in:
            with open(bundle_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return load_tck(bundle_path, reference=reference)
    else:
        raise FileNotFoundError(f"Could not find streamline file at {bundle_path_gz}")


def visualize_bundles(
    data_root,
    out_dir,
    subid,
    sesid,
    out_png,
    interactive=False,
    camera_positions=None,
):
    fa_img = nb.load(
        data_root
        / f"sub-{subid}"
        / f"ses-{sesid}"
        / "dwi"
        / f"sub-{subid}_ses-{sesid}_space-ACPC_model-tensor_param-fa_dwimap.nii.gz"
    )

    print("Loading arcuate fasciculus streamlines...")
    l_arc = get_bundle_data(
        data_root,
        subid,
        sesid,
        "AssociationArcuateFasciculusL",
        reference=fa_img,
    )
    r_arc = get_bundle_data(
        data_root,
        subid,
        sesid,
        "AssociationArcuateFasciculusR",
        reference=fa_img,
    )
    print("Loading cingulum streamlines...")
    l_cst = get_bundle_data(
        data_root,
        subid,
        sesid,
        "ProjectionBrainstemCorticospinalTractL",
        reference=fa_img,
    )
    r_cst = get_bundle_data(
        data_root,
        subid,
        sesid,
        "ProjectionBrainstemCorticospinalTractR",
        reference=fa_img,
    )
    # AssociationInferiorFrontoOccipitalFasciculusR
    r_inf_front_occipital = get_bundle_data(
        data_root,
        subid,
        sesid,
        "AssociationInferiorFrontoOccipitalFasciculusR",
        reference=fa_img,
    )
    l_inf_front_occipital = get_bundle_data(
        data_root,
        subid,
        sesid,
        "AssociationInferiorFrontoOccipitalFasciculusL",
        reference=fa_img,
    )

    print("Loading T1w reference image...")
    # Transform into the T1w reference frame
    t1w_img = nb.load(
        data_root
        / f"sub-{subid}"
        / f"ses-{sesid}"
        / "anat"
        / f"sub-{subid}_ses-{sesid}_space-ACPC_desc-preproc_T1w.nii.gz"
    )

    print("Loading brain mask...")
    # Load the brain mask - it will be shown as a translucent contour
    brain_mask_img = nb.load(
        data_root
        / f"sub-{subid}"
        / f"ses-{sesid}"
        / "anat"
        / f"sub-{subid}_ses-{sesid}_space-ACPC_desc-brain_mask.nii.gz"
    )
    brain_mask_data = brain_mask_img.get_fdata()
    # find the center of mass for the brain mask
    brain_mask_center = np.array(np.where(brain_mask_data))
    brain_mask_center = np.mean(brain_mask_center, axis=1)
    print(f"Brain mask center: {brain_mask_center}")

    print("Transforming streamlines to T1w space...")
    l_arc.to_rasmm()
    r_arc.to_rasmm()
    l_cst.to_rasmm()
    r_cst.to_rasmm()
    l_inf_front_occipital.to_rasmm()
    r_inf_front_occipital.to_rasmm()
    l_arc_t1w = transform_streamlines(l_arc.streamlines, np.linalg.inv(t1w_img.affine))
    r_arc_t1w = transform_streamlines(r_arc.streamlines, np.linalg.inv(t1w_img.affine))
    l_cst_t1w = transform_streamlines(l_cst.streamlines, np.linalg.inv(t1w_img.affine))
    r_cst_t1w = transform_streamlines(r_cst.streamlines, np.linalg.inv(t1w_img.affine))
    l_inf_front_occipital_t1w = transform_streamlines(
        l_inf_front_occipital.streamlines,
        np.linalg.inv(t1w_img.affine),
    )
    r_inf_front_occipital_t1w = transform_streamlines(
        r_inf_front_occipital.streamlines,
        np.linalg.inv(t1w_img.affine),
    )

    # Making a `scene`
    # -----------------
    # The next kind of fury object we will be working with is a `window.Scene`
    # object. This is the (3D!) canvas on which we are drawing the actors. We
    # initialize this object and call the `scene.add` method to add the actors.

    scene = window.Scene()

    brain_actor = actor.contour_from_roi(brain_mask_data, color=[0, 0, 0], opacity=0.1)

    scene.add(brain_actor)

    color_arc = tab20.colors[18]
    color_cst = tab20.colors[2]
    color_ifof = tab20.colors[8]

    l_arc_actor = lines_as_tubes(l_arc_t1w, 8, colors=color_arc)
    r_arc_actor = lines_as_tubes(r_arc_t1w, 8, colors=color_arc)
    l_cst_actor = lines_as_tubes(l_cst_t1w, 8, colors=color_cst)
    r_cst_actor = lines_as_tubes(r_cst_t1w, 8, colors=color_cst)
    l_inf_front_occipital_actor = lines_as_tubes(l_inf_front_occipital_t1w, 8, colors=color_ifof)
    r_inf_front_occipital_actor = lines_as_tubes(r_inf_front_occipital_t1w, 8, colors=color_ifof)

    scene.add(l_arc_actor)
    scene.add(r_arc_actor)
    scene.add(l_cst_actor)
    scene.add(r_cst_actor)
    scene.add(l_inf_front_occipital_actor)
    scene.add(r_inf_front_occipital_actor)

    scene.background((1, 1, 1))

    #############################################################################
    # Showing the visualization
    # -------------------------
    # If you are working in an interactive session, you can call::
    #
    # to see what the visualization looks like. This would pop up a window that will
    # show you the visualization as it is now. You can interact with this
    # visualization using your mouse to rotate the image in 3D, and mouse+ctrl or
    # mouse+shift to pan and rotate it in plane, respectively. Use the scroll up and
    # scroll down in your mouse to zoom in and out. Once you have found a view of
    # the data that you like, you can close the window (as long as its open, it is
    # blocking execution of any further commands in the Python interpreter!) and
    # then you can query your scene for the "camera settings" by calling::
    #
    #     scene.camera_info()
    #
    # This will print out to the screen something like this::
    #
    #     # Active Camera
    #        Position (238.04, 174.48, 143.04)
    #        Focal Point (96.32, 110.34, 84.48)
    #        View Up (-0.33, -0.12, 0.94)
    #
    # We can use the information we have gleaned to set the camera on subsequent
    # visualization that use this scene object.
    if interactive:
        print("Launching interactive visualization window...")
        window.show(scene, size=(1200, 1200), reset_camera=False)
        return scene

    images = []
    for position_name, position_info in camera_positions.items():
        png_path = out_dir / f"{out_png}_{position_name}.png"
        position = {
            "position": tuple(np.array(position_info["offset"]) + brain_mask_center),
            "focal_point": brain_mask_center,
            "view_up": position_info["view_up"],
        }
        print(f"\nSetting camera for {position_name}:")
        print(f"Position: {position['position']}")
        print(f"Focal point: {position['focal_point']}")
        print(f"View up: {position['view_up']}")
        scene.set_camera(**position)
        # Verify the camera was set correctly
        position, focal_point, view_up = scene.get_camera()
        print("Actual camera position after setting:")
        print(f"Position: {position}")
        print(f"Focal point: {focal_point}")
        print(f"View up: {view_up}")
        print(f"Saving visualization to {png_path}...")
        window.record(scene=scene, out_path=str(png_path), size=(2400, 2400), reset_camera=False)
        images.append(png_path)

    pf = PanelFigure(1, len(images), 3 * len(images), 3)
    png_path = out_dir / f"{out_png}.png"
    for n_image, image in enumerate(images):
        pf.add_img(image, n_image, 0)
    pf.format_and_save_figure(png_path)
    print("Done!")
    return images


if __name__ == "__main__":
    data_root = Path(
        "/cbica/projects/pafin/derivatives/qsirecon/derivatives/qsirecon-DSIAutoTrack"
    )
    out_dir = Path("/cbica/projects/pafin/code/figures")
    camera_positions6 = {
        "lh_camera_position": {
            "offset": (360.0, 0.0, 0.0),
            "view_up": (0.0, 0.0, 1.00),
        },
        "rh_camera_position": {
            "offset": (-360.0, 0.0, 0.0),
            "view_up": (0.0, 0.0, 1.00),
        },
        "posterior_camera_position": {
            "offset": (0.0, 360.0, 0.0),
            "view_up": (0.0, 0.0, 1.00),
        },
        "superior_camera_position": {
            "offset": (0.0, 0.0, 360.0),
            "view_up": (0.0, -1.0, 0.0),
        },
    }
    subjects = sorted(data_root.glob("sub-*"))
    for subject in subjects:
        subid = subject.name
        session_dirs = sorted(subject.glob("ses-*"))
        sesids = [session_dir.name for session_dir in session_dirs]
        for sesid in sesids:
            print(f"Processing {subid} {sesid}")
            images = visualize_bundles(
                data_root=data_root,
                out_dir=out_dir,
                subid=subid.replace("sub-", ""),
                sesid=sesid.replace("ses-", ""),
                out_png=f"QSIRecon_DSIAutoTrack_{subid}_{sesid}",
                camera_positions=camera_positions6,
            )
