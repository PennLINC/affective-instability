#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=48:00:00

/cbica/projects/pafin/.bashrc

mamba activate curation

bash 03_run_heudiconv.sh
python 04_convert_physio.py
python 05_copy_events.py
bash 06_chmod.sh
bash reface_t1ws.sh
bash 08_remove_face_files.sh
python 09_anonymize_acqtimes.py
python 10_clean_jsons.py
