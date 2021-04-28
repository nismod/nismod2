# Energy Demand (constrained)

[&lt; Back to Energy Demand](./energy-demand.html)

These details are for the "constrained" model configuration, which models
heating technology use in the demand model.

# Inputs

| description                            | name           | unit           | dims                                  | dtype   |
|:---------------------------------------|:---------------|:---------------|:--------------------------------------|:--------|
| Floor area, residential and commercial | floor_area     | meter**2       | ['lad_uk_2016', 'residential_or_non'] | float   |
| Minimum daily temperature              | t_min          | Degree Celcius | ['lad_uk_2016', 'yearday']            | float   |
| Maximum daily temperature              | t_max          | Degree Celcius | ['lad_uk_2016', 'yearday']            | float   |
| Population                             | population     | people         | ['lad_uk_2016']                       | float   |
| Regional Gross Value Added per capita  | gva_per_head   | GBP            | ['lad_uk_2016']                       | float   |
| Regional Gross Value Added, by sector  | gva_per_sector | GBP            | ['lad_uk_2016', 'sectors']            | float   |

# Parameters

| description                                        | name                       | unit    | dims                                                                        | dtype   |
|:---------------------------------------------------|:---------------------------|:--------|:----------------------------------------------------------------------------|:--------|
| Dwelling stock type or read in floor area directly | virtual_dw_stock           |         | nan                                                                         | bool    |
| Mode of model                                      | mode                       |         | nan                                                                         | int     |
| Service switches                                   | switches_service           |         | ['enduses_service_switch', 'tech', 'end_yr', 'sector']                      | float   |
| Generic fuel switch                                | generic_fuel_switch        |         | ['generic_switch_number', 'enduses', 'end_yr', 'param_generic_fuel_switch'] | float   |
| Share in cold rolling in steel manufacturing       | p_cold_rolling_steel       | decimal | ['end_yr', 'interpolation_params']                                          | float   |
| Recovered heat                                     | heat_recovered             | decimal | ['end_yr', 'interpolation_params', 'enduses']                               | float   |
| Share of cooled service floor area                 | cooled_floorarea           | decimal | ['end_yr', 'interpolation_params', 'enduses']                               | float   |
| Change in floor area per person                    | assump_diff_floorarea_pp   | decimal | ['end_yr', 'interpolation_params']                                          | float   |
| Air leakage caused reducing in demand              | air_leakage                | decimal | ['enduses', 'end_yr', 'interpolation_params']                               | float   |
| Efficiency achievement level                       | f_eff_achieved             | decimal | ['end_yr', 'interpolation_params']                                          | float   |
| Smart meter penetration                            | smart_meter_p              | decimal | ['end_yr', 'interpolation_params']                                          | float   |
| Residential base temperature                       | rs_t_base_heating          |         | ['interpolation_params', 'end_yr']                                          | float   |
| Service base temperature                           | ss_t_base_heating          |         | ['interpolation_params', 'end_yr']                                          | float   |
| Industrial base temperature                        | is_t_base_heating          |         | ['interpolation_params', 'end_yr']                                          | float   |
| Demand side management improvemnt                  | dm_improvement             |         | ['enduses', 'interpolation_params', 'end_yr']                               | float   |
| Spatial explicit diffusion or not                  | spatial_explicit_diffusion | integer | nan                                                                         | float   |
| Spatial diffusion speed                            | speed_con_max              |         | nan                                                                         | float   |
| Heat pump fractions                                | gshp_fraction              | decimal | ['interpolation_params', 'end_yr']                                          | float   |
| Heat pump fractions                                | gshp_fraction              | decimal | nan                                                                         | float   |
| Overall change in energy demand per enduse         | generic_enduse_change      | %       | ['enduses', 'interpolation_params', 'end_yr']                               | float   |

# Outputs

| description                                            | name                                                 | unit   | dims                      | dtype   |
|:-------------------------------------------------------|:-----------------------------------------------------|:-------|:--------------------------|:--------|
| Commercial solid fuel demand for boilers               | service_solid_fuel_boiler_solid_fuel                 | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential solid fuel demand for non-heating end uses | residential_solid_fuel_non_heating                   | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential solid fuel demand for boilers              | residential_solid_fuel_boiler_solid_fuel             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial solid fuel demand for boilers               | industry_solid_fuel_boiler_solid_fuel                | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial solid fuel demand for non-heating end uses  | service_solid_fuel_non_heating                       | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial solid fuel demand for non-heating end uses  | industry_solid_fuel_non_heating                      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial oil demand for non-heating end uses         | industry_oil_non_heating                             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential oil demand for boilers                     | residential_oil_boiler_oil                           | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial oil demand for boilers                      | industry_oil_boiler_oil                              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential oil demand for non-heating end uses        | residential_oil_non_heating                          | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial oil demand for boilers                      | service_oil_boiler_oil                               | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial oil demand for non-heating end uses         | service_oil_non_heating                              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential gas demand for boilers                     | residential_gas_boiler_gas                           | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential electricity demand for boilers             | residential_electricity_boiler_electricity           | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential oil demand for boilers                     | residential_oil_boiler_oil                           | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential biomass demand for boilers                 | residential_biomass_boiler_biomass                   | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential hydrogen demand for boilers                | residential_hydrogen_boiler_hydrogen                 | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential hydrogen demand for heat pumps             | residential_hydrogen_heat_pumps_hydrogen             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential electricity demand for heat pumps          | residential_electricity_heat_pumps_electricity       | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential gas demand for district heating/CHP        | residential_gas_district_heating_CHP_gas             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential electricity demand for district heating    | residential_electricity_district_heating_electricity | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential biomass demand for district heating        | residential_biomass_district_heating_biomass         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential hydrogen demand for district heating       | residential_hydrogen_district_heating_fuel_cell      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential hydrogen for fuel cells                    | residential_hydrogen_fuel_cell_hydrogen              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial solid_fuel demand for boilers               | service_solid_fuel_boiler_solid_fuel                 | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial gas demand for boilers                      | service_gas_boiler_gas                               | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial electricity demand for boilers              | service_electricity_boiler_electricity               | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial oil demand for boilers                      | service_oil_boiler_oil                               | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial biomass demand for boilers                  | service_biomass_boiler_biomass                       | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial hydrogen demand for boilers                 | service_hydrogen_boiler_hydrogen                     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial hydrogen demand for heat pumps              | service_hydrogen_heat_pumps_hydrogen                 | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial electricity demand for heat pumps           | service_electricity_heat_pumps_electricity           | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial gas demand for district heating             | service_gas_district_heating_CHP_gas                 | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial electricity demand for district heating     | service_electricity_district_heating_electricity     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial biomass demand for district heating         | service_biomass_district_heating_biomass             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial hydrogen demand for district heating        | service_hydrogen_district_heating_fuel_cell          | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial hydrogen for fuel cells                     | service_hydrogen_fuel_cell_hydrogen                  | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial solid_fuel demand for boilers               | industry_solid_fuel_boiler_solid_fuel                | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial gas demand for boilers                      | industry_gas_boiler_gas                              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial electricity demand for boilers              | industry_electricity_boiler_electricity              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial oil demand for boilers                      | industry_oil_boiler_oil                              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial biomass demand for boilers                  | industry_biomass_boiler_biomass                      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial hydrogen demand for boilers                 | industry_hydrogen_boiler_hydrogen                    | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial hydrogen demand for heat pumps              | industry_hydrogen_heat_pumps_hydrogen                | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial electricity demand for heat pumps           | industry_electricity_heat_pumps_electricity          | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial gas demand for district heating/CHP         | industry_gas_district_heating_CHP_gas                | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial electricity demand for district heating     | industry_electricity_district_heating_electricity    | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial biomass demand for district heating         | industry_biomass_district_heating_biomass            | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial hydrogen demand for district heating        | industry_hydrogen_district_heating_fuel_cell         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial hydrogen for fuel cells                     | industry_hydrogen_fuel_cell_hydrogen                 | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential solid fuel for non-heating end uses        | residential_solid_fuel_non_heating                   | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential gas for non-heating end uses               | residential_gas_non_heating                          | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential electricity for non-heating end uses       | residential_electricity_non_heating                  | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential oil for non-heating end uses               | residential_oil_non_heating                          | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential biomass for non-heating end uses           | residential_biomass_non_heating                      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential hydrogen for non-heating end uses          | residential_hydrogen_non_heating                     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial solid fuel for non-heating end uses         | service_solid_fuel_non_heating                       | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial gas for non-heating end uses                | service_gas_non_heating                              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial electricity for non-heating end uses        | service_electricity_non_heating                      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial oil for non-heating end uses                | service_oil_non_heating                              | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial biomass for non-heating end uses            | service_biomass_non_heating                          | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial hydrogen for non-heating end uses           | service_hydrogen_non_heating                         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial solid fuel for non-heating end uses         | industry_solid_fuel_non_heating                      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial gas for non-heating end uses                | industry_gas_non_heating                             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial electricity for non-heating end uses        | industry_electricity_non_heating                     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial oil for non-heating end uses                | industry_oil_non_heating                             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial biomass for non-heating end uses            | industry_biomass_non_heating                         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial hydrogen for non-heating end uses           | industry_hydrogen_non_heating                        | GW     | ['lad_uk_2016', 'hourly'] | float   |
