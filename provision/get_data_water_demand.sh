#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Define required directories and ensure they exist
temp_dir=$base_path/models/water_demand/temp
dim_dir=$base_path/data/dimensions/water_demand
data_dir=$base_path/data/scenarios/water_demand

mkdir -p $temp_dir
mkdir -p $dim_dir
mkdir -p $data_dir

# Download data
remote_data=water_demand/water_demand.zip
python $base_path/provision/get_data.py $remote_data $temp_dir

# Move the dimensions to the dimensions directory
mv $temp_dir/water_resource_zones.csv $dim_dir

# Move data to the scenario data directory
mv $temp_dir/constant_water_demand.csv $data_dir
mv $temp_dir/per_capita_water_demand.csv $data_dir
mv $temp_dir/water_resource_zone_populations.csv $data_dir

# Tidy up the temporary directory
rm -rf $temp_dir
