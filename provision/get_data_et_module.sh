#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
eval "$(grep -A3 "\[et-module\]" $base_path/provision/config.ini | tail -n3)"

# Download data
python $base_path/provision/get_data.py $remote_data $base_path/$local_dir

# Copy lad_gb_2016.shp to a more general location as it is used by more than just et_module
cp $base_path/data/et_module/dimensions/lad_gb_2016.* $base_path/data/dimensions/
