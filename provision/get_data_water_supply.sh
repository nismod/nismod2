#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Define required directories and ensure they exist
model_dir="${base_path}"/models/water_supply
download_dir="${model_dir}"/download
nodal_dir="${model_dir}"/nodal
dim_dir="${base_path}"/data/dimensions/water_supply
scenario_dir="${base_path}"/data/scenarios/water_supply
parameter_dir="${base_path}"/data/parameters/water_supply

mkdir -p "${download_dir}"
mkdir -p "${nodal_dir}"
mkdir -p "${dim_dir}"
mkdir -p "${scenario_dir}"
mkdir -p "${parameter_dir}"

# Download data
remote_data=water_supply/water_supply_data_v9.zip
python "${base_path}"/provision/get_data.py ${remote_data} "${download_dir}"

# Move all nodal input files
mv "${download_dir}"/installed_data/CatchmentIndex.csv "${nodal_dir}"
mv "${download_dir}"/installed_data/master_dynatop_points.csv "${nodal_dir}"
mv "${download_dir}"/installed_data/missing_data.csv "${nodal_dir}"
mv "${download_dir}"/installed_data/WRZ_DI_DO.csv "${nodal_dir}"

# Move all dimension definitions
mv "${download_dir}"/dimensions/borehole_names.csv "${dim_dir}"
mv "${download_dir}"/dimensions/cams_names.csv "${dim_dir}"
mv "${download_dir}"/dimensions/days_into_year.csv "${dim_dir}"
mv "${download_dir}"/dimensions/demand_nodes.csv "${dim_dir}"
mv "${download_dir}"/dimensions/demand_profile_zones.csv "${dim_dir}"
mv "${download_dir}"/dimensions/flow_file_column_names.csv "${dim_dir}"
mv "${download_dir}"/dimensions/global_variable_names.csv "${dim_dir}"
mv "${download_dir}"/dimensions/irrigations_cams_names.csv "${dim_dir}"
mv "${download_dir}"/dimensions/irrigations_file_column_names.csv "${dim_dir}"
mv "${download_dir}"/dimensions/months_into_year.csv "${dim_dir}"
mv "${download_dir}"/dimensions/nonpublic_use_codes.csv "${dim_dir}"
mv "${download_dir}"/dimensions/reservoir_names.csv "${dim_dir}"

# Move the scenario data
mv "${download_dir}"/scenarios/borehole_data.csv "${scenario_dir}"
mv "${download_dir}"/scenarios/flows_data.csv "${scenario_dir}"
mv "${download_dir}"/scenarios/irrigations_data.csv "${scenario_dir}"
mv "${download_dir}"/scenarios/reservoir_levels.csv "${scenario_dir}"

# Move the parameters data
mv "${download_dir}"/parameters/demand_profiles.csv "${parameter_dir}"
mv "${download_dir}"/parameters/nonpublic_water_demands.csv "${parameter_dir}"
