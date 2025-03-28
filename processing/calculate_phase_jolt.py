"""Calculate phase jolt and phase jump time series from phase data."""

import os
import shutil
import subprocess
from glob import glob

import nibabel as nb
import numpy as np
import templateflow.api as tfapi
from fmriprep.interfaces.resampling import ResampleSeries


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/dset"
    temp_dir = "/cbica/comp_space/pafin/phase_jolt"
    out_dir = "/cbica/projects/pafin/derivatives/phase_jolt"
    fmriprep_dir = "/cbica/projects/pafin/derivatives/fmriprep"

    ref_file = tfapi.get(
        "MNI152NLin2009cAsym",
        resolution="02",
        desc=None,
        suffix="T1w",
        extension=".nii.gz",
    )

    os.makedirs(temp_dir, exist_ok=True)

    for subject_dir in glob(os.path.join(in_dir, "sub-*"))[:1]:
        subid = os.path.basename(subject_dir)
        print(subid)

        for session_dir in glob(os.path.join(subject_dir, "ses-*")):
            sesid = os.path.basename(session_dir)
            print(f"\t{sesid}")

            out_sub_dir = os.path.join(out_dir, subid, sesid, "func")
            os.makedirs(out_sub_dir, exist_ok=True)

            phase_files = sorted(
                glob(os.path.join(session_dir, "func", "*echo-1*part-phase_bold.nii.gz"))
            )
            for phase_file in phase_files:
                print(f"\t\t{os.path.basename(phase_file)}")
                echo_files = sorted(glob(phase_file.replace("echo-1", "echo-*")))
                phase_jump_files = []
                phase_jolt_files = []
                phase_laplacian_files = []

                for echo_file in echo_files:
                    base_name = os.path.basename(echo_file)
                    out_prefix = os.path.join(
                        temp_dir,
                        base_name.replace("_part-phase_bold.nii.gz", ""),
                    )

                    cmd = (
                        "/cbica/projects/pafin/laynii/LN2_PHASE_JOLT "
                        f"-input {echo_file} -int13 -phase_jump -2D -output {out_prefix}"
                    )
                    print(cmd)
                    subprocess.run(
                        cmd.split(),
                    )
                    phase_jump_file = out_prefix + "_phase_jump.nii"
                    phase_jolt_file = out_prefix + "_phase_jolt.nii"
                    assert os.path.isfile(phase_jump_file)
                    assert os.path.isfile(phase_jolt_file)

                    cmd = (
                        "/cbica/projects/pafin/laynii/LN2_PHASE_LAPLACIAN "
                        f"-input {echo_file} -int13 -2D -output {out_prefix}"
                    )
                    print(cmd)
                    subprocess.run(
                        cmd.split(),
                    )
                    phase_laplacian_file = out_prefix + "_phase_laplacian.nii"
                    assert os.path.isfile(phase_laplacian_file)

                    out_phase_jump_file = os.path.join(
                        out_sub_dir,
                        base_name.replace("_bold.nii.gz", "_desc-jump_bold.nii.gz"),
                    )
                    out_phase_jolt_file = os.path.join(
                        out_sub_dir,
                        base_name.replace("_bold.nii.gz", "_desc-jolt_bold.nii.gz"),
                    )
                    out_phase_laplacian_file = os.path.join(
                        out_sub_dir,
                        base_name.replace("_bold.nii.gz", "_desc-laplacian_bold.nii.gz"),
                    )

                    nb.load(phase_jump_file).to_filename(out_phase_jump_file)
                    nb.load(phase_jolt_file).to_filename(out_phase_jolt_file)
                    nb.load(phase_laplacian_file).to_filename(out_phase_laplacian_file)
                    phase_jump_files.append(out_phase_jump_file)
                    phase_jolt_files.append(out_phase_jolt_file)
                    phase_laplacian_files.append(out_phase_laplacian_file)
                    del phase_jump_file, phase_jolt_file, phase_laplacian_file
                    del out_phase_jump_file, out_phase_jolt_file, out_phase_laplacian_file

                print("\t\tAveraging phase jumps")
                base_name = os.path.basename(phase_file)
                avg_phase_jump_file = os.path.join(
                    out_sub_dir,
                    base_name.replace("echo-1_", "").replace("_bold", "_desc-jump_bold"),
                )
                arrs = [nb.load(f).get_fdata() for f in phase_jump_files]
                avg_phase_jump = np.mean(arrs, axis=0)
                base_img = nb.load(phase_jump_files[0])
                nb.Nifti1Image(avg_phase_jump, base_img.affine, base_img.header).to_filename(
                    avg_phase_jump_file
                )
                del arrs, avg_phase_jump
                phase_jump_files.append(avg_phase_jump_file)

                print("\t\tAveraging phase jolts")
                avg_phase_jolt_file = os.path.join(
                    out_sub_dir,
                    base_name.replace("echo-1_", "").replace("_bold", "_desc-jolt_bold"),
                )
                arrs = [nb.load(f).get_fdata() for f in phase_jolt_files]
                avg_phase_jolt = np.mean(arrs, axis=0)
                base_img = nb.load(phase_jolt_files[0])
                nb.Nifti1Image(avg_phase_jolt, base_img.affine, base_img.header).to_filename(
                    avg_phase_jolt_file
                )
                del arrs, avg_phase_jolt
                phase_jolt_files.append(avg_phase_jolt_file)

                print("\t\tAveraging phase laplacians")
                avg_phase_laplacian_file = os.path.join(
                    out_sub_dir,
                    base_name.replace("echo-1_", "").replace("_bold", "_desc-laplacian_bold"),
                )
                arrs = [nb.load(f).get_fdata() for f in phase_laplacian_files]
                avg_phase_laplacian = np.mean(arrs, axis=0)
                base_img = nb.load(phase_laplacian_files[0])
                nb.Nifti1Image(avg_phase_laplacian, base_img.affine, base_img.header).to_filename(
                    avg_phase_laplacian_file
                )
                del arrs, avg_phase_laplacian
                phase_laplacian_files.append(avg_phase_laplacian_file)

                # Now apply HMC+coreg+norm transforms to the phase jolt and jump files
                # Get the HMC+coreg+norm transforms
                fmriprep_sub_dir = os.path.join(fmriprep_dir, subid, sesid)
                new_base_name = base_name.split("_echo-")[0]
                hmc_file = os.path.join(
                    fmriprep_sub_dir,
                    "func",
                    f"{new_base_name}_from-orig_to-boldref_mode-image_desc-hmc_xfm.txt",
                )
                coreg_file = os.path.join(
                    fmriprep_sub_dir,
                    "func",
                    f"{new_base_name}_from-boldref_to-T1w_mode-image_desc-coreg_xfm.txt",
                )
                norm_file = os.path.join(
                    fmriprep_sub_dir,
                    "anat",
                    f"{subid}_{sesid}_rec-norm_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5",
                )

                # Apply the transforms to the phase jolt and jump files
                for phase_jump_file in phase_jump_files:
                    print(f"\t\tWarping {os.path.basename(phase_jump_file)}")
                    out_fname = os.path.basename(phase_jump_file).replace(
                        "desc-",
                        "space-MNI152NLin2009cAsym_desc-",
                    )
                    out_phase_jump_file = os.path.join(out_sub_dir, out_fname)
                    resampler = ResampleSeries(
                        jacobian=False,
                        in_file=phase_jump_file,
                        ref_file=ref_file,
                        transforms=[hmc_file, coreg_file, norm_file],
                    )
                    result = resampler.run(cwd=temp_dir)
                    shutil.copyfile(result.outputs.out_file, out_phase_jump_file)

                for phase_jolt_file in phase_jolt_files:
                    print(f"\t\tWarping {os.path.basename(phase_jolt_file)}")
                    out_fname = os.path.basename(phase_jolt_file).replace(
                        "desc-",
                        "space-MNI152NLin2009cAsym_desc-",
                    )
                    out_phase_jolt_file = os.path.join(out_sub_dir, out_fname)
                    resampler = ResampleSeries(
                        jacobian=False,
                        in_file=phase_jolt_file,
                        ref_file=ref_file,
                        transforms=[hmc_file, coreg_file, norm_file],
                    )
                    result = resampler.run(cwd=temp_dir)
                    shutil.copyfile(result.outputs.out_file, out_phase_jolt_file)

                for phase_jolt_file in phase_jolt_files:
                    print(f"\t\tWarping {os.path.basename(phase_laplacian_file)}")
                    out_fname = os.path.basename(phase_laplacian_file).replace(
                        "desc-",
                        "space-MNI152NLin2009cAsym_desc-",
                    )
                    out_phase_laplacian_file = os.path.join(out_sub_dir, out_fname)
                    resampler = ResampleSeries(
                        jacobian=False,
                        in_file=phase_laplacian_file,
                        ref_file=ref_file,
                        transforms=[hmc_file, coreg_file, norm_file],
                    )
                    result = resampler.run(cwd=temp_dir)
                    shutil.copyfile(result.outputs.out_file, out_phase_laplacian_file)
