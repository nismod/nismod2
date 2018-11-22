#!/usr/bin/env bash

base_path=$1

# Install tkinter as requirement for matplotlib
apt-get install -y python3-tk

# Setup wrapper
printf "[PATHS]\n" > $base_path/models/energy_demand/wrapperconfig.ini
printf "path_local_data = $base_path/data/energy_demand\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_processed_data = $base_path/data/energy_demand/_processed_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_result_data = $base_path/data/energy_demand/results\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "[CONFIG]\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "base_yr = 2015\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "weather_yr_scenario = 2015\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "user_defined_simulation_end_yr = 2050\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "user_defined_weather_by = 2015\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "[CRITERIA]\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "mode_constrained = True\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "virtual_building_stock_criteria = True\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "write_out_national = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "reg_selection = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "MSOA_crit = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "reg_selection_csv_name = msoa_regions_ed.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "spatial_calibration = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "cluster_calc = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "write_txt_additional_results = True\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "validation_criteria = True\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "plot_crit = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "crit_plot_enduse_lp = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "writeYAML_keynames = True\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "writeYAML = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "crit_temp_min_max = False\n" >> $base_path/models/energy_demand/wrapperconfig.ini

# pip3 install -e /vagrant/models/energy_demand
source <(grep = <(grep -A3 "\[energy-demand\]" $base_path/provision/config.ini))
pip3 install energy_demand==$release

# Prepare directory for data
mkdir -p "$target"

. $base_path/provision/get_data.sh energy-demand $base_path

# Post install
energy_demand minimal_setup -d $base_path/data/energy_demand
