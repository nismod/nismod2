#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read remote_data from config.ini
eval "$(grep -A2 "\[water-demand\]" $base_path/provision/config.ini | tail -n2)"

# Define required directories and ensure they exist
temp_dir=$base_path/models/water_demand/temp
dim_dir=$base_path/data/dimensions/water_demand
data_dir=$base_path/data/scenarios/water_demand

mkdir -p $temp_dir
mkdir -p $dim_dir
mkdir -p $data_dir

# Download data
python $base_path/provision/get_data.py $remote_data $temp_dir

# Move the dimensions to the dimensions directory
mv $temp_dir/dimensions/water_resource_zones.csv $dim_dir
mv $temp_dir/dimensions/WRMP_WRZ.cpg $dim_dir
mv $temp_dir/dimensions/WRMP_WRZ.dbf $dim_dir
mv $temp_dir/dimensions/WRMP_WRZ.prj $dim_dir
mv $temp_dir/dimensions/WRMP_WRZ.shp $dim_dir
mv $temp_dir/dimensions/WRMP_WRZ.shp.xml $dim_dir
mv $temp_dir/dimensions/WRMP_WRZ.shx $dim_dir

# Move data to the scenario data directory
mv $temp_dir/scenarios/constant_water_demand__BL.csv $data_dir
mv $temp_dir/scenarios/per_capita_water_demand__BL.csv $data_dir
mv $temp_dir/scenarios/constant_water_demand__FP.csv $data_dir
mv $temp_dir/scenarios/per_capita_water_demand__FP.csv $data_dir
mv $temp_dir/scenarios/water_resource_zone_populations.csv $data_dir

# Tidy up the temporary directory
rm -rf $temp_dir
