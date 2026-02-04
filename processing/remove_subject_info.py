#!/usr/bin/env python3
"""
remove_subject_info.py
Removes subject information from .bin files by removing everything after ":"
in the Subject Info section, until the "Subject Notes:" line.
"""

import os
import re
from pathlib import Path

# Define directories
root_dir = "/Volumes/pafin/sourcedata/actigraphy/sourcedata"
input_dir = os.path.join(root_dir, "raw")
output_base_dir = os.path.join(root_dir, "anonymized")

# Find all .bin files recursively in subdirectories
bin_files = list(Path(input_dir).glob("**/*.bin"))

if not bin_files:
    print(f"No .bin files found in {input_dir}")
    exit(1)

print(f"Found {len(bin_files)} bin files to process\n")

# Process each file
for bin_file in bin_files:
    print(f"Processing: {bin_file.name}")
    
    # Extract subject ID from filename (remove .bin extension)
    # Handle both "12345.bin" and "sub-12345.bin" formats
    subject_id = bin_file.stem  # filename without extension
    if subject_id.startswith("sub-"):
        subject_id = subject_id[4:]  # Remove "sub-" prefix if present
    
    # Create output path: sourcedata/sub-<ID>/actigraphy/<original_filename>.bin
    subject_label = f"sub-{subject_id}"
    output_file = Path(output_base_dir) / subject_label / "actigraphy" / bin_file.name
    
    # Check if output file already exists
    if output_file.exists():
        print(f"  Output file already exists: {output_file}")
        print(f"  Skipping {bin_file.name}\n")
        continue
    
    try:
        # Read the file
        with open(bin_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Find and process Subject Info section
        in_subject_info = False
        modified = False
        
        for i, line in enumerate(lines):
            # Check if we're entering the Subject Info section
            if re.match(r'^Subject Info', line, re.IGNORECASE):
                in_subject_info = True
                print(f"  Found Subject Info section at line {i+1}")
            
            # Process lines in Subject Info section
            if in_subject_info:
                # Check if this is "Subject Notes:" - process it and then stop
                if re.match(r'^Subject Notes:', line, re.IGNORECASE):
                    # Remove everything after the colon
                    lines[i] = line.split(':')[0] + ':\n'
                    modified = True
                    print(f"  Reached end of Subject Info section at line {i+1} (Subject Notes)")
                    in_subject_info = False
                elif ':' in line:
                    # Remove everything after the colon (keep label and colon)
                    lines[i] = line.split(':')[0] + ':\n'
                    modified = True
                elif line.strip() == '':
                    # Empty line - end of Subject Info (but only if we've already processed Subject Notes)
                    in_subject_info = False
        
        # Create output subdirectories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"  ✓ Saved to: {output_file}\n")
        
    except Exception as e:
        print(f"  ✗ Error: {e}\n")

print(f"Finished processing {len(bin_files)} files")
print(f"Output base directory: {output_base_dir}")

