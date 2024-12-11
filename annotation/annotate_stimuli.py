"""Automatically annotate stimuli with a series of feature extractors from pliers."""

import importlib
import json
import os
from glob import glob

import pandas as pd
from pliers.stimuli import VideoStim

extraction_module = importlib.import_module('pliers.extractors')


def annotate_file(in_file, out_dir):
    """Apply extractors to a stimulus file."""
    config_file = 'general_features.json'
    with open(config_file) as fo:
        transformer_list = json.load(fo)

    video_stim = VideoStim(in_file)

    for transformer_config in transformer_list:
        xfm_cfg = transformer_config[0]
        transformer_name = xfm_cfg['transformer']
        params = xfm_cfg.get('parameters', {})

        print(f'Applying transformer: {transformer_config}')

        transformer = getattr(extraction_module, transformer_name)(**params)
        results = transformer.transform(video_stim)
        result_dfs = [res.to_df() for res in results]
        result_df = pd.concat(result_dfs)
        result_df.to_csv(
            os.path.join(out_dir, f'{transformer_name}.tsv'),
            sep='\t',
            index=False,
            na_rep='n/a',
        )


def main():
    """Annotate stimuli with pliers."""
    in_dir = '/cbica/projects/pafin/sourcedata/stimuli'
    files = sorted(glob(os.path.join(in_dir, '*.mp4')))
    for f in files:
        annotate_file(f, '/cbica/projects/pafin/derivatives/pliers')
