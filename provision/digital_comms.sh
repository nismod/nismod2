#!/usr/bin/env bash

source <(grep = <(grep -A3 "\[digital-comms\]" /vagrant/provision/config.ini))
pip3 install git+https://github.com/nismod/digital_comms.git@$release#egg=digital_comms

# Post install
source <(grep = <(grep -A3 '\[ftp-config\]' /vagrant/provision/ftp.ini))

# Prepare directory for data
mkdir -p "$target"

# Download data
. /vagrant/provision/get_data.sh digital-comms

# Copy region definitions to smif region_definition
mkdir /vagrant/data/region_definitions/assets_broadband_network
cp /vagrant/data/digital_comms/assets_layer3_cabinets.* /vagrant/data/region_definitions/assets_broadband_network/
cp /vagrant/data/digital_comms/assets_layer4_distributions.* /vagrant/data/region_definitions/assets_broadband_network/