#!/usr/bin/env bash

# Install tkinter as requirement for matplotlib
apt-get install -y python3-tk

# pip3 install -e /vagrant/models/energy_demand
source <(grep = <(grep -A3 "\[energy-demand\]" /vagrant/provision/config.ini))
pip3 install energy_demand==$release

# Post install
source <(grep = <(grep -A3 '\[ftp-config\]' /vagrant/provision/ftp.ini))

# Prepare directory for data
mkdir -p "$target"

. /vagrant/provision/get_data.sh energy-demand

# Post install
energy_demand minimal_setup -d /vagrant/data_energy_demand
