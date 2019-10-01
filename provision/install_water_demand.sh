#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version from config.ini
eval "$(grep -A2 "\[water-demand\]" $base_path/provision/config.ini | tail -n2)"

# Install directly from GitHub
pip install git+https://github.com/nismod/water_demand.git@$model_version#egg=water_demand --upgrade
