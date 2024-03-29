#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read remote_data, local_dir from config.ini
eval "$(grep -A3 "\[digital-comms\]" $base_path/provision/config.ini | tail -n3)"
local_path=$base_path/$local_dir

# Download data
python $base_path/provision/get_data.py $remote_data $local_path

# Copy region definitions to smif region_definition
mkdir -p $base_path/data/region_definitions/assets_broadband_network
cp $base_path/data/digital_comms/processed/assets_layer3_cabinets.* $base_path/data/region_definitions/assets_broadband_network/
cp $base_path/data/digital_comms/processed/assets_layer4_distributions.* $base_path/data/region_definitions/assets_broadband_network/
