import os
import subprocess
from glob import glob

out_dir = "/cbica/projects/pafin/ds006131"
in_dir = "/cbica/projects/pafin/test/ds006131"

files = sorted(glob(os.path.join(in_dir, "sub-*", "ses-*", "func", "*_physio.tsv.gz")))
print(len(files))
for in_file in files:
    print(in_file)
    out_file = in_file.replace(in_dir, out_dir)
    assert in_file != out_file
    cmd = f"cp -RL {in_file} {out_file}"
    subprocess.run(cmd.split(" "))
