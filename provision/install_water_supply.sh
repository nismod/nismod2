#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Define required directories and ensure they exist
model_dir="${base_path}"/models/water_supply
repo_dir="${model_dir}"/repo
nodal_dir="${model_dir}"/nodal
exe_dir="${model_dir}"/exe

mkdir -p "${repo_dir}"
mkdir -p "${nodal_dir}"
mkdir -p "${exe_dir}"

# Clone repo and copy necessary files to the model directory
git clone git@github.com:nismod/water_supply.git "${repo_dir}" || exit
pushd "${repo_dir}" || exit
    # Pin the model at a specific commit
    git checkout 02eca9f81e0bbd2ffdb7f4963e70da8163c24646
popd || exit

# Move the files necessary for execution
mv "${repo_dir}"/wathnet/w5_console.exe "${exe_dir}"
mv "${repo_dir}"/models/National_Model.wat "${exe_dir}"

# Seems to be necessary to add execution to the wathnet exe
chmod +x "${exe_dir}"/w5_console.exe

# Move the prepare_nodal script
mv "${repo_dir}"/scripts/preprocessing/prepare_nodal.py "${nodal_dir}"

# Clean up the cloned repo
rm -rf "${repo_dir}"
