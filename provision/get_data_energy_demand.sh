#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Core data
source <(grep = <(grep -A3 "\[energy-demand\]" $base_path/provision/config.ini))
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path

# Config data
source <(grep = <(grep -A3 "\[energy-demand-config-data\]" $base_path/provision/config.ini))
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path
