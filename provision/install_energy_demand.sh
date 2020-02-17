#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
eval "$(grep -A3 "\[energy-demand\]" $base_path/provision/config.ini | tail -n3)"

# Install energy_demand
pip install git+https://github.com/nismod/energy_demand.git@$model_version#egg=energy_demand --upgrade

# Setup wrapper config
wrapperconfig_path=$base_path/models/energy_demand/wrapperconfig.ini
cat > $wrapperconfig_path << EOF
[PATHS]
path_local_data = $base_path/data/energy_demand
path_processed_data = $base_path/data/energy_demand/_processed_data
path_result_data = $base_path/data/energy_demand/results
path_new_scenario = $base_path/data/energy_demand/results/tmp_model_run_results

[CONFIG]
base_yr = 2015
weather_yr_scenario = 2015
user_defined_simulation_end_yr = 2050
user_defined_weather_by = 2015

[CRITERIA]
cluster_calc = False
mode_constrained = True
# If floor area is read from a scenario, virtual_building_stock_criteria should be False
virtual_building_stock_criteria = True
write_out_national = False
reg_selection = False
MSOA_crit = False
reg_selection_csv_name = msoa_regions_ed.csv
spatial_calibration = True
write_txt_additional_results = True
validation_criteria = True
plot_crit = False
crit_plot_enduse_lp = False
writeYAML_keynames = True
writeYAML = False
crit_temp_min_max = True
constant_weather = False

[DATA_PATHS]
local_path_datafolder = $base_path/data/energy_demand
path_strategy_vars = $base_path/data/energy_demand/00_user_defined_variables
#ONS principal projection
path_population_data_for_disaggregation_LAD = $base_path/data/energy_demand/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050.csv
#ONS principal projection
folder_raw_carbon_trust = $base_path/data/energy_demand/_raw_data/G_Carbon_Trust_advanced_metering_trial/
path_population_data_for_disaggregation_MSOA = $base_path/data/energy_demand/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050_MSOA_lad.csv
path_floor_area_virtual_stock_by = $base_path/data/energy_demand/_raw_data/K-floor_area/floor_area_LAD_latest.csv
path_assumptions_db = $base_path/data/energy_demand/_processed_data/assumptions_from_db
data_processed = $base_path/data/energy_demand/_processed_data
lad_shapefile = $base_path/data/energy_demand/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp
path_post_installation_data = $base_path/data/energy_demand/_processed_data
weather_data = /raw_data/A-temperature_data/cleaned_weather_stations_data
load_profiles = $base_path/data/energy_demand/_processed_data/load_profiles
rs_load_profile_txt = $base_path/data/energy_demand/_processed_data/load_profiles/rs_submodel
ss_load_profile_txt = $base_path/data/energy_demand/_processed_data/load_profiles/ss_submodel
yaml_parameters = $base_path/data/energy_demand/config/yaml_parameters.yml
yaml_parameters_constrained = $base_path/data/energy_demand/config/yaml_parameters_constrained.yml
yaml_parameters_keynames_constrained = $base_path/data/energy_demand/config/yaml_parameters_keynames_constrained.yml
yaml_parameters_keynames_unconstrained = $base_path/data/energy_demand/config/yaml_parameters_keynames_unconstrained.yml
yaml_parameters_scenario = $base_path/data/energy_demand/config/yaml_parameters_scenario.yml

[CONFIG_DATA]
path_main = $base_path/data/energy_demand/config_data
# Path to all technologies
path_technologies = $base_path/data/energy_demand/config_data/05-technologies/technology_definition.csv
# Paths to fuel raw data
rs_fuel_raw = $base_path/data/energy_demand/config_data/02-fuel_base_year/rs_fuel.csv
ss_fuel_raw = $base_path/data/energy_demand/config_data/02-fuel_base_year/ss_fuel.csv
is_fuel_raw = $base_path/data/energy_demand/config_data/02-fuel_base_year/is_fuel.csv
# Load profiles
lp_rs = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/HES_lp.csv
# Technologies load shapes
path_hourly_gas_shape_resid = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_gas_boiler_dh_SANSOM.csv
lp_elec_hp_dh = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_elec_hp_dh_LOVE.csv
lp_all_microCHP_dh = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_all_microCHP_dh_SANSOM.csv
path_shape_rs_cooling = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/shape_residential_cooling.csv
path_shape_ss_cooling = $base_path/data/energy_demand/config_data/03-load_profiles/ss_submodel/shape_service_cooling.csv
lp_elec_storage_heating = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_elec_storage_heating_HESReport.csv
lp_elec_secondary_heating = $base_path/data/energy_demand/config_data/03-load_profiles/rs_submodel/lp_elec_secondary_heating_HES.csv
# Census data
path_employment_statistics = $base_path/data/energy_demand/config_data/04-census_data/LAD_census_data.csv
# Validation datasets
val_subnational_elec = $base_path/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec.csv
val_subnational_elec_residential = $base_path/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec_domestic.csv
val_subnational_elec_non_residential = $base_path/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec_non_domestic.csv
val_subnational_elec_msoa_residential = $base_path/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/MSOA_domestic_electricity_2015_cleaned.csv
val_subnational_elec_msoa_non_residential = $base_path/data/energy_demand/config_data/01-validation_datasets/02_subnational_elec/MSOA_non_dom_electricity_2015_cleaned.csv
val_subnational_gas = $base_path/data/energy_demand/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas.csv
val_subnational_gas_residential = $base_path/data/energy_demand/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas_domestic.csv
val_subnational_gas_non_residential = $base_path/data/energy_demand/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas_non_domestic.csv
val_nat_elec_data = $base_path/data/energy_demand/config_data/01-validation_datasets/01_national_elec_2015/elec_demand_2015.csv

[RESULT_DATA]
data_results = $base_path/data/energy_demand/results/
data_results_model_run_pop = $base_path/data/energy_demand/results/model_run_pop
data_results_model_runs = $base_path/data/energy_demand/results/model_run_results_txt
data_results_PDF = $base_path/data/energy_demand/results/PDF_results
data_results_validation = $base_path/data/energy_demand/results/PDF_validation
model_run_pop = $base_path/data/energy_demand/results/model_run_pop
data_results_shapefiles = $base_path/data/energy_demand/results/spatial_results
individual_enduse_lp = $base_path/data/energy_demand/results/individual_enduse_lp
EOF
