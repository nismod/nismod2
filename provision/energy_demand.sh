#!/usr/bin/env bash

base_path=$1

# Install tkinter as requirement for matplotlib
apt-get install -y python3-tk

# Setup wrapper
printf "[PATHS]\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_local_data = /vagrant/data/energy_demand\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_processed_data = /vagrant/data/energy_demand/_processed_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_result_data = /vagrant/data/energy_demand/results\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_config_data = /vagrant/data/energy_demand/config_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_new_scenario = /vagrant/data/energy_demand/results/tmp_model_run_results\n" >> $base_path/models/energy_demand/wrapperconfig.ini
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
printf "crit_temp_min_max = True\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "[DATA_PATHS]\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "local_path_datafolder = /vagrant/data/energy_demand/energy_demand_minimal\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_strategy_vars = /vagrant/data/energy_demand/energy_demand_minimal/00_user_defined_variables\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "#ONS principal projection\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_population_data_for_disaggregation_LAD = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050.csv  \n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "#ONS principal projection\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "folder_raw_carbon_trust = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/G_Carbon_Trust_advanced_metering_trial/\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_population_data_for_disaggregation_MSOA = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050_MSOA_lad.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "folder_path_weater_stations = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/A-temperature_data/cleaned_weather_stations.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_floor_area_virtual_stock_by = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/K-floor_area/floor_area_LAD_latest.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_assumptions_db = /vagrant/data/energy_demand/_processed_data/assumptions_from_db\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_processed = /vagrant/data/energy_demand/_processed_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "lad_shapefile = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_post_installation_data = /vagrant/data/energy_demand/_processed_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "weather_data = /raw_data/A-temperature_data/cleaned_weather_stations_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "load_profiles = /vagrant/data/energy_demand/_processed_data/load_profiles\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "rs_load_profile_txt = /vagrant/data/energy_demand/_processed_data/load_profiles/rs_submodel\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "ss_load_profile_txt = /vagrant/data/energy_demand/_processed_data/load_profiles/ss_submodel\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "yaml_parameters = /vagrant/data/energy_demand/config/yaml_parameters.yml\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "yaml_parameters_constrained = /vagrant/data/energy_demand/config/yaml_parameters_constrained.yml\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "yaml_parameters_keynames_constrained = /vagrant/data/energy_demand/config/yaml_parameters_keynames_constrained.yml\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "yaml_parameters_keynames_unconstrained = /vagrant/data/energy_demand/config/yaml_parameters_keynames_unconstrained.yml\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "yaml_parameters_scenario = /vagrant/data/energy_demand/config/yaml_parameters_scenario.yml\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "[CONFIG_DATA]\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_main = /vagrant/data/energy_demand/config_data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "# Path to all technologies\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_technologies = /vagrant/data/energy_demand/config_data/05-technologies/technology_definition.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "# Paths to fuel raw data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "rs_fuel_raw = /vagrant/data/energy_demand/config_data/02-fuel_base_year/rs_fuel.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "ss_fuel_raw = /vagrant/data/energy_demand/config_data/02-fuel_base_year/ss_fuel.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "is_fuel_raw = /vagrant/data/energy_demand/config_data/02-fuel_base_year/is_fuel.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "# Load profiles\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "lp_rs = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/HES_lp.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "# Technologies load shapes\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_hourly_gas_shape_resid = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_gas_boiler_dh_SANSOM.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "lp_elec_hp_dh = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_elec_hp_dh_LOVE.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "lp_all_microCHP_dh = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_all_microCHP_dh_SANSOM.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_shape_rs_cooling = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/shape_residential_cooling.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_shape_ss_cooling = /vagrant/data/energy_demand/config_data/03-load_profiles/ss_submodel/shape_service_cooling.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "lp_elec_storage_heating = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_elec_storage_heating_HESReport.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "lp_elec_secondary_heating = /vagrant/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_elec_secondary_heating_HES.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "# Census data\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "path_employment_statistics = /vagrant/data/energy_demand/config_data/04-census_data/LAD_census_data.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "# Validation datasets\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_elec = /vagrant/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_elec_residential = /vagrant/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec_domestic.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_elec_non_residential = /vagrant/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec_non_domestic.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_elec_msoa_residential = /vagrant/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/MSOA_domestic_electricity_2015_cleaned.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_elec_msoa_non_residential = /vagrant/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/MSOA_non_dom_electricity_2015_cleaned.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_gas = /vagrant/data/energy_demand/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_gas_residential = /vagrant/data/energy_demand/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas_domestic.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_subnational_gas_non_residential = /vagrant/data/energy_demand/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas_non_domestic.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "val_nat_elec_data = /vagrant/data/energy_demand/config_data/01-validation_datasets/01_national_elec_2015/elec_demand_2015.csv\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "[RESULT_DATA]\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_results = /vagrant/data/energy_demand/results/\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_results_model_run_pop = /vagrant/data/energy_demand/results/model_run_pop\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_results_model_runs = /vagrant/data/energy_demand/results/model_run_results_txt\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_results_PDF = /vagrant/data/energy_demand/results/PDF_results\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_results_validation = /vagrant/data/energy_demand/results/PDF_validation\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "model_run_pop = /vagrant/data/energy_demand/results/model_run_pop\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "data_results_shapefiles = /vagrant/data/energy_demand/results/spatial_results\n" >> $base_path/models/energy_demand/wrapperconfig.ini
printf "individual_enduse_lp = /vagrant/data/energy_demand/results/individual_enduse_lp\n" >> $base_path/models/energy_demand/wrapperconfig.ini


pip3 install -e /vagrant/models/energy_demand
source <(grep = <(grep -A3 "\[energy-demand\]" $base_path/provision/config.ini))
pip3 install energy_demand==$release

# Prepare directory for data
mkdir -p "$target"

. $base_path/provision/get_data.sh energy-demand $base_path

# Post install
energy_demand minimal_setup -d $base_path/data/energy_demand
