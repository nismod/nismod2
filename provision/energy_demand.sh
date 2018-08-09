#!/usr/bin/env bash

base_path=$1

# Install tkinter as requirement for matplotlib
apt-get install -y python3-tk

# Setup wrapper
printf "[PATHS]\n" > $base_path/models/energy_demand/wrapperconfig.ini
printf "path_local_data = $base_path/data/energy_demand\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_processed_data = $base_path/data/energy_demand/_processed_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_result_data = $base_path/data/energy_demand/results\n" >> $base_path/models/energy_demand/wrapperconfig.ini

# pip3 install -e /vagrant/models/energy_demand
source <(grep = <(grep -A3 "\[energy-demand\]" $base_path/provision/config.ini))
pip3 install energy_demand==$release

# Prepare directory for data
mkdir -p "$target"

. $base_path/provision/get_data.sh energy-demand $base_path

# Post install
energy_demand minimal_setup -d $base_path/data/energy_demand
