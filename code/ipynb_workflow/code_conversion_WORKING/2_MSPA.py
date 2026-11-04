# How to Run MSPA.py
# Overview
# MSPA.py runs GWB_MSPA (GuidosToolbox Workbench - Morphological Spatial Pattern Analysis) via WSL. It takes preprocessed binary rasters and classifies foreground pixels into spatial pattern categories (core, edge, bridge, loop, branch, islet, perforation).

# This script runs outside the Docker container, directly on Windows with WSL.

# Prerequisites
# Windows with WSL — wsl command must be accessible from PowerShell
# GWB installed in WSL — GWB_MSPA must be on the WSL PATH. On first use, type yes to accept the license.
# Preprocessed input rasters — 8-bit GeoTIFFs with foreground=2, background=1, nodata=0. Use MSPA_preprocessing.ipynb (in Docker) to prepare these.
# Python 3 on Windows — only uses os and subprocess (standard library)
# Workflow
# MSPA_preprocessing.ipynb (Docker) → MSPA.py (Windows/WSL)
# Setup
# Edit paths in MSPA.py:

# input_dir = r"D:\typology\data\DS_TEST\mosaic_P_recoded"
# output_dir = r"D:\typology\data\DS_TEST\MSPA"
# Run from PowerShell
# cd D:\typology\code\DS_code_conversion
# python MSPA.py
# Important Notes
# Clear the output folder before each run — leftover log files will cause failure
# First-time use: type yes for the GWB license
# Input must be strictly 8-bit with values 1 (background) and 2 (foreground)
# The script auto-converts Windows paths to WSL paths




import os
import subprocess

# wsl terminal
# cd ~
#wsl
#GWB_MSPA

#powershell terminal
# cd D:\typology\code\DS_code_conversion
# python MSPA.py

# N O T E:
# if first time using type "yes" to accept the GWB license agreement
# make sure that the output folder does not contain any log files from previous runs, it will fail to run

# Folders - use absolute paths
input_dir = r"D:\typology\data\DS_TEST\mosaic_P_recoded"
output_dir = r"D:\typology\data\DS_TEST\MSPA"
os.makedirs(output_dir, exist_ok=True)

# MSPA parameters
# connectivity (8), edge- default (1), transition- off (0), intext = on (1), write to disk with swap (1), statistics- off (0)
params = """8 
1
0
1
1
1
0"""

with open(os.path.join(input_dir, "mspa-parameters.txt"), "w") as f:
    f.write(params)

# convert windows paths to WSL path
input_wsl = subprocess.check_output(["wsl", "wslpath", "-u", input_dir.replace("\\", "/")], text=True).strip()
output_wsl = subprocess.check_output(["wsl", "wslpath", "-u", output_dir.replace("\\", "/")], text=True).strip()

# GWB_MSPA in WSL
subprocess.run([
    "wsl", "GWB_MSPA",
    f"-i={input_wsl}",
    f"-o={output_wsl}"
], check=True)