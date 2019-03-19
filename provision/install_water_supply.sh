#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[water-supply\]" $base_path/provision/config.ini))

# Locations for the git repo (temporary) and the nodal-related files
repo_dir=$local_dir/repo
nodal_dir=$local_dir/nodal

# Clone repo and copy necessary files to the model directory
mkdir -p $repo_dir
git clone --depth 1 git@github.com:nismod/water_supply.git $repo_dir || exit "$?"

cp $repo_dir/wathnet/w5_console.exe $local_dir
cp $repo_dir/models/National_Model.wat $local_dir

# Seems to be necessary to add execution to the wathnet exe
chmod +x $repo_dir/wathnet/w5_console.exe

# Copy files needed for creating nodal file. This will be superseded by data being fed directly.
mkdir -p $nodal_dir
cp $local_dir/repo/scripts/preprocessing/prepare_nodal.py $nodal_dir

python $base_path/provision/get_data.py $remote_data $nodal_dir

# Clean up the cloned repo
rm -rf $repo_dir

