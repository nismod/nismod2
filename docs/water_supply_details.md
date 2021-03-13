# Water Supply

Water resources model for England and Wales.

# Inputs

| description              | name             | unit   | dims                                                                                                                 | dtype   |
|:-------------------------|:-----------------|:-------|:---------------------------------------------------------------------------------------------------------------------|:--------|
| Public water demand      | water_demand     | Ml/day | ['water_resource_zones']                                                                                             | float   |
| Reservoir storage levels | reservoir_levels | Ml     | ['water_supply/reservoir_names']                                                                                     | float   |
| Stream flows             | flows_data       | Ml/day | ['water_supply/days_into_year', 'water_supply/flow_file_column_names']                                               | float   |
| Irrigation demand        | irrigations_data | Ml/day | ['water_supply/days_into_year', 'water_supply/irrigations_cams_names', 'water_supply/irrigations_file_column_names'] | float   |
| Borehole data            | borehole_data    | Ml/day | ['water_supply/months_into_year', 'water_supply/borehole_names']                                                     | float   |

# Parameters

| description            | name                   | unit   | dims                                                                 | dtype   |
|:-----------------------|:-----------------------|:-------|:---------------------------------------------------------------------|:--------|
| Nonpublic water demand | nonpublic_water_demand | Ml/day | ['water_supply/cams_names', 'water_supply/nonpublic_use_codes']      | float   |
| Demand profiles        | demand_profiles        | None   | ['water_supply/days_into_year', 'water_supply/demand_profile_zones'] | float   |

# Outputs

| description                                                            | name                                 | unit                      | dims                                                                  | dtype   |
|:-----------------------------------------------------------------------|:-------------------------------------|:--------------------------|:----------------------------------------------------------------------|:--------|
| Reservoir storage levels (this is used as input to the next timestep)  | reservoir_levels                     | Ml                        | ['water_supply/reservoir_names']                                      | float   |
| Daily reservoir levels                                                 | water_supply_reservoir_daily_volumes | Ml                        | ['water_supply/days_into_year', 'water_supply/reservoir_names']       | float   |
| Global variables (including level of service for Water Resource Zones) | water_supply_global_variables        | Unknown/possibly variable | ['water_supply/days_into_year', 'water_supply/global_variable_names'] | float   |
| Demand as modelled                                                     | water_supply_requested_demand        | Ml                        | ['water_supply/days_into_year', 'water_supply/demand_nodes']          | float   |
| Shortfall                                                              | water_supply_shortfall               | Ml                        | ['water_supply/days_into_year', 'water_supply/demand_nodes']          | float   |
