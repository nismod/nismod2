# Transport (road)

Road transport model for Great Britain.

# Inputs

| description                                                         | name                   | unit   | dims                            | dtype   |
|:--------------------------------------------------------------------|:-----------------------|:-------|:--------------------------------|:--------|
| Population                                                          | population             | people | ['lad_gb_2016']                 | float   |
| Regional Gross Value Added (rGVA)                                   | gva                    | GBP    | ['lad_gb_2016']                 | float   |
| Fuel prices                                                         | fuel_price             | £/l    | ['transport_fuel_type']         | float   |
| Fuel price (electricity)                                            | fuel_price_electricity | £/kWh  | nan                             | float   |
| Link travel time                                                    | link_travel_time       | h      | nan                             | float   |
| Vehicle fleet composition (engine type proportion per vehicle type) | engine_type_fractions  | nan    | ['vehicle_type', 'engine_type'] | float   |

# Parameters

| description                                                                                 | name                              | unit   | dims   | dtype   |
|:--------------------------------------------------------------------------------------------|:----------------------------------|:-------|:-------|:--------|
| Population elasticity for passenger demand                                                  | POPULATION_ETA                    |        |        | float   |
| GVA elasticity for passenger demand                                                         | GVA_ETA                           |        |        | float   |
| Time elasticity for passenger demand                                                        | TIME_ETA                          |        |        | float   |
| Cost elasticity for passenger demand                                                        | COST_ETA                          |        |        | float   |
| Population elasticity for freight demand                                                    | POPULATION_FREIGHT_ETA            |        |        | float   |
| GVA elasticity for freight demand                                                           | GVA_FREIGHT_ETA                   |        |        | float   |
| Time elasticity for freight demand                                                          | TIME_FREIGHT_ETA                  |        |        | float   |
| Cost elasticity for freight demand                                                          | COST_FREIGHT_ETA                  |        |        | float   |
| Averages link travel time with the time from previous iterations (1.0 = overwrite with new) | link_travel_time_averaging_weight |        |        | float   |
| How many times to repeat the same assignment to obtain average times                        | assignment_iterations             |        |        | int     |
| How many times to iterate between flow prediction and flow assignment                       | prediction_iterations             |        |        | int     |
| Whether to use route-choice model (true) or routing with A-Star (false)                     | use_route_choice_model            |        |        | bool    |

# Outputs

| description                                       | name                                     | unit   | dims                                  | dtype   |
|:--------------------------------------------------|:-----------------------------------------|:-------|:--------------------------------------|:--------|
| Energy consumption (liquid fuels)                 | energy_consumption                       | l      | ['annual_day', 'transport_fuel_type'] | float   |
| Energy consumption (electricity)                  | energy_consumption_electricity           | kWh    | ['annual_day']                        | float   |
| Energy consumption (electricity, by start zone)   | electric_vehicle_electricity_consumption | kWh    | ['lad_gb_2016', 'annual_day_hours']   | float   |
| Electric vehicle trips                            | electric_vehicle_trip_starts             | trips  | ['lad_gb_2016', 'annual_day_hours']   | int     |
| Link travel time (used as input to next timestep) | link_travel_time                         | h      | nan                                   | float   |
