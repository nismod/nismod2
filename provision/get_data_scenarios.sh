#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Climate scenarios
eval "$(grep -A3 "\[climate\]" $base_path/provision/config.ini | tail -n3)"
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path

# ITRC population and gva scenarios
eval "$(grep -A3 "\[population\]" $base_path/provision/config.ini | tail -n3)"
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path

# Prices scenarios
eval "$(grep -A3 "\[prices\]" $base_path/provision/config.ini | tail -n3)"
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path

# Dwellings, GVA, Population, Floor Area scenarios
eval "$(grep -A3 "\[socio-economic\]" $base_path/provision/config.ini | tail -n3)"
local_path=$base_path/$local_dir
rm -r $local_path/socio-economic-*
python $base_path/provision/get_data.py $remote_data $local_path
mv $local_path/socio-economic-*/* $local_path
rm -r $local_path/socio-economic-*

# EV transport trips
eval "$(grep -A3 "\[ev_transport_trips\]" $base_path/provision/config.ini | tail -n3)"
local_path=$base_path/$local_dir
python $base_path/provision/get_data.py $remote_data $local_path
