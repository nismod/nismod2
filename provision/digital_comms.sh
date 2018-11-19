#!/usr/bin/env bash

base_path=$1

source <(grep = <(grep -A3 "\[digital-comms\]" $base_path/provision/config.ini))
pip3 install git+https://github.com/nismod/digital_comms.git@$release#egg=digital_comms

# Setup wrapper
printf "[PATHS]\npath_local_data = $base_path/data/digital_comms/processed\n" > $base_path/models/digital_comms/wrapperconfig.ini

# Prepare directory for data
mkdir -p "$target"

# Download data
. $base_path/provision/get_data.sh digital-comms $base_path

# Copy region definitions to smif region_definition
mkdir -p $base_path/data/region_definitions/assets_broadband_network
cp $base_path/data/digital_comms/assets_layer3_cabinets.* $base_path/data/region_definitions/assets_broadband_network/
cp $base_path/data/digital_comms/assets_layer4_distributions.* $base_path/data/region_definitions/assets_broadband_network/
