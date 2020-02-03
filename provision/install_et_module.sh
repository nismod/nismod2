#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
eval "$(grep -A3 "\[et-module\]" $base_path/provision/config.ini | tail -n3)"

# Install energy_demand
pip install git+https://github.com/nismod/et_module.git@$model_version#egg=et_module --upgrade

# Copy lad_gb_2016.shp to a more general location as it is used by more than just et_module
cp $base_path/data/et_module/dimensions/lad_gb_2016.shp $base_path/data/dimensions/lad_gb_2016.shp
