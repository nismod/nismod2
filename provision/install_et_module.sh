#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
eval "$(grep -A3 "\[et-module\]" $base_path/provision/config.ini | tail -n3)"

# Install energy_demand
pip install git+https://github.com/nismod/et_module.git@$model_version#egg=et_module --upgrade
