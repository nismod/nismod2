# Transport (rail)

Transport rail model for Great Britain.

# Inputs

| description                       | name                    | unit   | dims            | dtype   |
|:----------------------------------|:------------------------|:-------|:----------------|:--------|
| Population                        | population              | people | ['lad_gb_2016'] | float   |
| Regional Gross Value Added (rGVA) | gva                     | GBP    | ['lad_gb_2016'] | float   |
| Station usage (day)               | day_usage               | people | ['NLC_gb']      | float   |
| Station usage (year)              | year_usage              | people | ['NLC_gb']      | int     |
| Fares                             | rail_journey_fares      | £      | ['NLC_gb']      | float   |
| Journey times                     | rail_journey_times      | h      | ['NLC_gb']      | float   |
| Car journey costs                 | car_zonal_journey_costs | £      | ['lad_gb_2016'] | float   |
| Rail trip rates                   | rail_trip_rates         | nan    | nan             | float   |

# Parameters

| description                                                      | name                            | unit   | dims                  | dtype   |
|:-----------------------------------------------------------------|:--------------------------------|:-------|:----------------------|:--------|
| Population elasticity for passenger demand                       | elasticities                    |        | ['variables', 'area'] | float   |
| Whether to use output of road model for car costs                | use_car_cost_from_road_model    |        | nan                   | bool    |
| Wether to predict all years between base year and predicted year | predict_intermediate_rail_years |        | nan                   | bool    |
| Station usage numbers for the base year                          | base_year_year_demand           |        | ['NLC_gb']            | int     |
| Station usage numbers for the base year                          | base_year_day_demand            |        | ['NLC_gb']            | float   |

# Outputs

| description                      | name                         | unit   | dims            | dtype   |
|:---------------------------------|:-----------------------------|:-------|:----------------|:--------|
| Station usage (year)             | year_stations_usage          | people | ['NLC_gb']      | int     |
| Station usage (day)              | day_stations_usage           | people | ['NLC_gb']      | float   |
| Total zonal rail demand (year)   | total_year_zonal_rail_demand | people | ['lad_gb_2016'] | float   |
| Average zonal rail demand (year) | avg_year_zonal_rail_demand   | people | ['lad_gb_2016'] | float   |
| Total zonal rail demand (day)    | total_day_zonal_rail_demand  | people | ['lad_gb_2016'] | float   |
| Average zonal rail demand (day)  | avg_day_zonal_rail_demand    | people | ['lad_gb_2016'] | float   |
