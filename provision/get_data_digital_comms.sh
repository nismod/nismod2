#!/usr/bin/env bash

base_path=$1

# Download data
. $base_path/provision/get_data.sh digital-comms $base_path

# Copy region definitions to smif region_definition
mkdir -p $base_path/data/region_definitions/assets_broadband_network
cp $base_path/data/digital_comms/assets_layer3_cabinets.* $base_path/data/region_definitions/assets_broadband_network/
cp $base_path/data/digital_comms/assets_layer4_distributions.* $base_path/data/region_definitions/assets_broadband_network/
