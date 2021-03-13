# Energy Supply

These details are for the "unconstrained/optimised" model configuration, which
models heating technology use in the supply model.

# Inputs

| description                               | name                   | unit    | dims                            | dtype   |
|:------------------------------------------|:-----------------------|:--------|:--------------------------------|:--------|
| Electricity demand                        | elecload               | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Gas demand                                | gasload                | mcm     | ['gas_nodes', 'seasonal_week']  | float   |
| Residential heat demand                   | heatload_res           | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Residential non-heat gas demand           | gasload_non_heat_res   | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| Residential non-heat electricity demand   | elecload_non_heat_res  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Commercial heat demand                    | heatload_com           | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Commercial non-heat gas demand            | gasload_non_heat_com   | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| Commerical non-heat electricity demand    | elecload_non_heat_com  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Non-heat hydrogen demand                  | hydrogen_non_heat_eh   | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Non-heat oil demand                       | oil_non_heat_eh        | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Non-heat solid fuel demand                | solid_fuel_non_heat_eh | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Fuel prices                               | fuel_price             | GBP/MWh | ['seasons', 'es_fuel_types']    | float   |
| Wind speed at energy hubs                 | wind_speed_eh          | m/s     | ['energy_hub', 'seasonal_week'] | float   |
| Wind speed at bus bars                    | wind_speed_bus         | m/s     | ['bus_bars', 'seasonal_week']   | float   |
| Insolation at bus bars                    | insolation_bus         | W/m2    | ['bus_bars', 'seasonal_week']   | float   |
| Insolation at energy hubs                 | insolation_eh          | W/m2    | ['energy_hub', 'seasonal_week'] | float   |
| Electric Vehicle Vehicle-to-Grid capacity | EV_Cap                 | MW      | ['energy_hub']                  | float   |
| Electricity demand for transport          | elec_trans             | MWh     | ['energy_hub', 'seasonal_week'] | float   |
| Hydrogen demand for transport             | hydrogen_trans         | MWh     | ['energy_hub', 'seasonal_week'] | float   |
| Biomass feedstock                         | biomass_feedstock      | kg      | ['energy_hub']                  | float   |
| Municipal waste supply                    | municipal_waste        | kg      | ['energy_hub']                  | float   |
| Electricity interconnector prices         | elec_int               | £/MW    | ['elec_intercon_countries']     | float   |

# Parameters

| description                                                                       | name                 | unit   | dims   | dtype   |
|:----------------------------------------------------------------------------------|:---------------------|:-------|:-------|:--------|
| Cost of electricity load shedding                                                 | LoadShed_elec        |        |        | float   |
| Cost of gas load shedding                                                         | LoadShed_gas         |        |        | float   |
| Flag to configure heat technology mode                                            | heat_mode            |        |        | int     |
| Flag to configure central/decentral operation mode                                | operation_mode       |        |        | int     |
| Flag to configure heat supply strategy in the optimised mode                      | heat_supply_strategy |        |        | int     |
| Flag to setup the sensitivity study in the optimised mode                         | sensitivity_mode     |        |        | int     |
| Flag to turn on/off emissions constraint                                          | emissions_constraint |        |        | int     |
| Flag to enable/disable smart charging capability                                  | ev_smart_charging    |        |        | int     |
| Flag to enable/disable ev vehicle to grid services                                | ev_vehicle_to_grid   |        |        | int     |
| Flag to enable/disable unit commitment function of thermal electricity generators | unit_commitment      |        |        | int     |

# Outputs

| description                                       | name                            | unit    | dims                            | dtype   |
|:--------------------------------------------------|:--------------------------------|:--------|:--------------------------------|:--------|
| Gas-fired generation                              | tran_gas_fired                  | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Coal-fired generation                             | tran_coal                       | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Pumped storage generation                         | tran_pump_power                 | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Hydro-electric generation                         | tran_hydro                      | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Nuclear generation                                | tran_nuclear                    | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Interconnector imports (electricity)              | tran_int_import                 | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Interconnector exports (electricity)              | tran_int_export                 | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Renewable generation (transmission-connected)     | tran_renewable                  | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Cost of electricity                               | elec_cost                       | GBP/kWh | ['national', 'seasonal_week']   | float   |
| Electricity reserve                               | e_reserve                       | MW      | ['national', 'seasonal_week']   | float   |
| Domestic gas                                      | gas_domestic                    | mcm     | ['national', 'seasonal_week']   | float   |
| Liquified Natural Gas                             | gas_lng                         | mcm     | ['national', 'seasonal_week']   | float   |
| Interconnector gas                                | gas_interconnector              | mcm     | ['national', 'seasonal_week']   | float   |
| Shale gas                                         | gas_shale                       | mcm     | ['national', 'seasonal_week']   | float   |
| Gas storage                                       | gas_storage_level               | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| Onshore wind generation (transmission-connected)  | tran_wind_onshore               | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Offshore wind generation (transmission-connected) | tran_wind_offshore              | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Solar generation (transmission-connected)         | tran_pv_power                   | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Wind curtailed (transmission-connected)           | tran_wind_curtailed             | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Solar curtailed (transmission-connected)          | tran_pv_curtailed               | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Total optimisation cost                           | total_opt_cost                  | GBP     | ['national', 'seasonal_week']   | float   |
| Total optimisation cost of transmission           | total_opt_cost_transmission     | GBP     | ['national', 'seasonal_week']   | float   |
| Total optimisation cost of distribution           | total_opt_cost_distribution     | GBP     | ['energy_hub', 'seasonal_week'] | float   |
| Gas-fired/other generation (energy hub)           | eh_gas_fired_other              | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Wind generation (energy hub)                      | eh_wind_power                   | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Wind curtailed (energy hub)                       | eh_wind_curtailed               | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Solar generation (energy hub)                     | eh_pv_power                     | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Solar curtailed (energy hub)                      | eh_pv_curtailed                 | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Gas load shed                                     | gas_load_shed                   | mcm     | ['gas_nodes', 'seasonal_week']  | float   |
| Electricity load shed                             | elec_load_shed                  | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Electricity emissions (transmission connected)    | e_emissions                     | t       | ['bus_bars', 'seasonal_week']   | float   |
| Electricity emissions (energy hub)                | e_emissions_eh                  | t       | ['energy_hub', 'seasonal_week'] | float   |
| Heat emissions (energy hub)                       | h_emissions_eh                  | t       | ['energy_hub', 'seasonal_week'] | float   |
| Gas load shed (energy hub)                        | gas_load_shed_eh                | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| Electricity load shed (energy hub)                | elec_load_shed_eh               | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Fresh water demand (for cooling)                  | fresh_water_demand              | MW      | ['bus_bars', 'seasonal_week']   | float   |
| Combined Heat and Power Gas (energy hub)          | eh_chp_gas                      | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Combined Heat and Power Biomass (energy hub)      | eh_chp_biomass                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Combined Heat and Power Waste (energy hub)        | eh_chp_waste                    | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Fuel Cell (energy hub)                            | eh_fuel_cell                    | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Gas demand for heat (energy hub)                  | gasdemand_heat                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| Electricity demand for heat (energy hub)          | elecdemand_heat                 | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_gasboiler_b                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_gasboiler_dh                 | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_gaschp_dh                    | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_heatpump_b                   | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_heatpump_dh                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_electricboiler_b             | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_electricboiler_dh            | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_biomassboiler_b              | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_biomassboiler_dh             | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_biomasschp_dh                | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_wastechp_dh                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_hydrogenboiler_b             | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_hydrogen_fuelcell_dh         | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_hydrogen_heatpump_b          | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | gas_injection                   | mcm     | ['national', 'seasonal_week']   | float   |
| nan                                               | gas_withdraw                    | mcm     | ['national', 'seasonal_week']   | float   |
| nan                                               | eh_tran_e                       | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_tran_g                       | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_gas_qs                       | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_gstorage_level               | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_h2                           | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_h2_qs                        | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_h2storage_level              | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | gas_demand                      | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | electricity_demand              | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | biomass_demand                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | hydrogen_demand                 | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | waste_demand                    | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | solidfuel_demand                | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | oil_demand                      | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | gas_demand_heat                 | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | electricity_demand_heat         | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | biomass_demand_heat             | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | hydrogen_demand_heat            | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | waste_demand_heat               | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | solidfuel_demand_heat           | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | oil_demand_heat                 | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | ev_storage                      | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | ev_flowin                       | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | ev_flowout                      | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_tran_e_export                | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | e_uc                            | MW      | ['national', 'seasonal_week']   | float   |
| nan                                               | tran_gas_ccs                    | MW      | ['bus_bars', 'seasonal_week']   | float   |
| nan                                               | tran_oil                        | MW      | ['bus_bars', 'seasonal_week']   | float   |
| nan                                               | eh_oil                          | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_hybridhp_hp                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_hybridhp_gb                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_resistive_b                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_oilboiler_b                  | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_h2_smr                       | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_h2_electrolysis              | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | ev_v2g                          | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | ev_g2v                          | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | ev_charging                     | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_h2_blend_vol                 | mcm     | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_biogas_blend_vol             | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | dsm_shifted_demand              | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | dsm_assigned_demand             | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | dsm_electricity_demand          | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | other_emissions_eh              | t       | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | hydrogen_emissions_eh           | t       | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | total_emissions                 | t       | ['national', 'seasonal_week']   | float   |
| nan                                               | net_emissions                   | t       | ['national', 'seasonal_week']   | float   |
| nan                                               | tran_beccs                      | MW      | ['bus_bars', 'seasonal_week']   | float   |
| nan                                               | tran_h2ccgt                     | MW      | ['bus_bars', 'seasonal_week']   | float   |
| nan                                               | hydrogen_demand_transport       | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_battery_supply               | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | eh_battery_charge               | MW      | ['energy_hub', 'seasonal_week'] | float   |
| nan                                               | gas_demand_national             | MW      | ['national', 'seasonal_week']   | float   |
| nan                                               | electricity_demand_national     | MW      | ['national', 'seasonal_week']   | float   |
| nan                                               | dsm_electricity_demand_national | MW      | ['national', 'seasonal_week']   | float   |
| nan                                               | biomass_demand_national         | MW      | ['national', 'seasonal_week']   | float   |
