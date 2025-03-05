% A template MATLAB script to run NORDIC on a magnitude+phase file pair.
% I used {{ X }} to define variables that will be filled in by the Python wrapper script.
% Settings come from Thomas Madison.

% Set args as recommended for fMRI
% set to 0 if input includes both magnitude + phase timeseries
ARG.magnitude_only = {{ magnitude_only }};
% save out the phase data too
ARG.make_complex_nii = {{ make_complex_nii }};
% set to 1 for fMRI
ARG.temporal_phase = 1;
% set to 1 to enable NORDIC denoising
ARG.NORDIC = 1;
% use 10 for fMRI
ARG.phase_filter_width = 10;
% set equal to number of noise frames at end of scan, if present
ARG.noise_volume_last = {{ n_noise_vols }};
% DIROUT may need to be separate from fn_out
ARG.DIROUT = '{{ out_dir }}';

fn_magn_in = '{{ mag_file }}';
fn_phase_in = '{{ phase_file }}';
fn_out = '{{ out_prefix }}'

% Add the NORDIC code
% Using https://github.com/nipreps/NORDIC_Raw/blob/6c5d9c754879c8d582349bf8a25dd432e2785220/NIFTI_NORDIC.m
addpath('/cbica/projects/pafin/NORDIC_Raw')

% Call NORDIC on the input files
NIFTI_NORDIC(fn_magn_in, fn_phase_in, fn_out, ARG)
