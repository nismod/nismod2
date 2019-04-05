#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Climate scenarios
source <(grep = <(grep -A3 "\[climate\]" $base_path/provision/config.ini))
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path

# Population and gva scenarios
source <(grep = <(grep -A3 "\[population\]" $base_path/provision/config.ini))
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path

# Prices scenarios
source <(grep = <(grep -A3 "\[prices\]" $base_path/provision/config.ini))
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path