import os
from glob import glob

import pandas as pd

cwd = os.getcwd()
os.chdir("/cbica/projects/pafin/derivatives/qsirecon/derivatives/qsirecon-DSIAutoTrack")
files = sorted(glob("sub-*/ses-1/dwi/*_streamlines.tck.gz"))
bundles = [f.split("bundle-")[1].split("_")[0] for f in files]
bundles = sorted(set(bundles))
subjects = sorted(glob("sub-*"))
df = pd.DataFrame(columns=subjects, index=bundles)
for sub in subjects:
   for bundle in bundles:
      streamline_files = sorted(glob(f"{sub}/ses-1/dwi/*_bundle-{bundle}_streamlines.tck.gz"))
      df.loc[bundle, sub] = bool(len(streamline_files))

df2 = df.loc[~df.all(axis=1)]
os.chdir(cwd)
df2.to_csv("bundles.tsv", sep="\t", index_label="bundle")
