# Energy Demand

These details are for the "unconstrained/optimised" model configuration, which
models heating technology use in the supply model.

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

| description                    | name                    | unit   | dims                      | dtype   |
|:-------------------------------|:------------------------|:-------|:--------------------------|:--------|
| Residential solid fuel demand  | residential_solid_fuel  | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential gas demand         | residential_gas         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential electricity demand | residential_electricity | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential oil demand         | residential_oil         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential biomass demand     | residential_biomass     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential hydrogen demand    | residential_hydrogen    | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Residential heat demand        | residential_heat        | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial solid fuel demand   | service_solid_fuel      | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial gas demand          | service_gas             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial electricity demand  | service_electricity     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial oil demand          | service_oil             | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial biomass demand      | service_biomass         | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial hydrogen demand     | service_hydrogen        | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Commercial heat demand         | service_heat            | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial solid fuel demand   | industry_solid_fuel     | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial gas demand          | industry_gas            | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial electricity demand  | industry_electricity    | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial oil demand          | industry_oil            | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial biomass demand      | industry_biomass        | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial hydrogen demand     | industry_hydrogen       | GW     | ['lad_uk_2016', 'hourly'] | float   |
| Industrial heat demand         | industry_heat           | GW     | ['lad_uk_2016', 'hourly'] | float   |
