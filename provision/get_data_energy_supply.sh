#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[energy-supply\]" $base_path/provision/config.ini))

# Download data
python3 $base_path/provision/get_data.py $remote_data $base_path/$local_dir
