#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read remote_data, local_dir from config.ini
eval "$(grep -A4 "\[water-supply\]" $base_path/provision/config.ini | tail -n3)"

# Ensure the directory exists
nodal_dir=$local_dir/nodal
mkdir -p $nodal_dir

# Download data
python $base_path/provision/get_data.py $remote_data $nodal_dir
