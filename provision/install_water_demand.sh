#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read remote_data, local_dir from config.ini
eval "$(grep -A2 "\[water-demand\]" $base_path/provision/config.ini | tail -n2)"

# Locations for the git repo (temporary) and the nodal-related files
repo_dir=$local_dir/repo

# Clone repo and copy necessary files to the model directory
pip install git+https://github.com/nismod/water_demand.git@$model_version#egg=water_demand
