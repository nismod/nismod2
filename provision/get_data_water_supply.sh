#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Define required directories and ensure they exist
model_dir=${base_path}/models/water_supply
download_dir=${model_dir}/download
nodal_dir=${model_dir}/nodal
dim_dir=${base_path}/data/dimensions/water_supply
scenario_dir=${base_path}/data/scenarios/water_supply

mkdir -p ${download_dir}
mkdir -p ${nodal_dir}
mkdir -p ${dim_dir}
mkdir -p ${scenario_dir}

# Download data
remote_data=water_supply/water_supply_data_v6.zip
python ${base_path}/provision/get_data.py ${remote_data} ${download_dir}

# Move all nodal input files
mv ${download_dir}/001_daily.csv ${nodal_dir}
mv ${download_dir}/borehole_forcing_1974_to_2015.csv ${nodal_dir}
mv ${download_dir}/cams_mean_daily_returns.csv ${nodal_dir}
mv ${download_dir}/CatchmentIndex.csv ${nodal_dir}
mv ${download_dir}/Demand_Profiles.csv ${nodal_dir}
mv ${download_dir}/master_dynatop_points.csv ${nodal_dir}
mv ${download_dir}/missing_data.csv ${nodal_dir}
mv ${download_dir}/National_WRSM_NatModel_logNSE_obs_11018_1.txt ${nodal_dir}
mv ${download_dir}/WRZ_DI_DO.csv ${nodal_dir}

# Move all dimension definitions
mv ${download_dir}/days_into_year.csv ${dim_dir}
mv ${download_dir}/water_supply_arcs.csv ${dim_dir}
mv ${download_dir}/water_supply_demand_nodes.csv ${dim_dir}
mv ${download_dir}/water_supply_global_variable_names.csv ${dim_dir}
mv ${download_dir}/water_supply_reservoirs.csv ${dim_dir}

# Move the scenario data (initial reservoir volumes
mv ${download_dir}/reservoir_levels.csv ${scenario_dir}
