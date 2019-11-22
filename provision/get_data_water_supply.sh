#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read data version from config.ini
eval "$(grep -A4 "\[water-supply\]" $base_path/provision/config.ini | tail -n4)"

# Define required directories and ensure they exist
model_dir="${base_path}"/models/water_supply
download_dir="${model_dir}"/download
nodal_dir="${model_dir}"/nodal
dim_dir="${base_path}"/data/dimensions/water_supply
scenario_dir="${base_path}"/data/scenarios/water_supply
parameter_dir="${base_path}"/data/parameters/water_supply
interventions_dir="${base_path}"/data/interventions
strategies_dir="${base_path}"/data/strategies

mkdir -p "${download_dir}"
mkdir -p "${nodal_dir}"
mkdir -p "${dim_dir}"
mkdir -p "${scenario_dir}"
mkdir -p "${parameter_dir}"

# Download data
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
mv "${download_dir}"/scenarios/*.parquet "${scenario_dir}"
mv "${download_dir}"/scenarios/reservoir_levels.csv "${scenario_dir}"

# Move the parameters data
mv "${download_dir}"/parameters/demand_profiles.csv "${parameter_dir}"
mv "${download_dir}"/parameters/nonpublic_water_demands.csv "${parameter_dir}"

# Move interventions and strategies
mv "${download_dir}"/interventions/arc_ws_options.csv $interventions_dir
mv "${download_dir}"/strategies/arc_ws__opt_* $strategies_dir

# Fix up a zero-th strategy
cp $strategies_dir/arc_ws__opt_1.csv $strategies_dir/arc_ws__opt_0.csv
sed -i 's/1/0/g' $strategies_dir/arc_ws__opt_0.csv
