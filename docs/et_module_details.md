# Energy-Transport (et_module)

[&lt; Back to Transport](./transport.html)

Derives energy demand and Vehicle-to-Grid (V2G) capacity from transport model
electric vehicle outputs.

# Inputs

| description                             | name           | unit   | dims                                | dtype   |
|:----------------------------------------|:---------------|:-------|:------------------------------------|:--------|
| Electricity demand of electric vehicles | ev_electricity | kWh    | ['lad_gb_2016', 'annual_day_hours'] | float   |
| Trip count of electric vehicles         | ev_trips       | trips  | ['lad_gb_2016', 'annual_day_hours'] | int     |

# Parameters

| description                                                 | name                         | unit   | dims   | dtype   |
|:------------------------------------------------------------|:-----------------------------|:-------|:-------|:--------|
| Year until future load profile assignment is fully realised | yr_until_changed_lp          |        |        | float   |
| Electric Vehicle charging regime                            | load_profile_charging_regime |        |        | float   |

# Outputs

| description                             | name             | unit   | dims            | dtype   |
|:----------------------------------------|:-----------------|:-------|:----------------|:--------|
| Vehicle-to-Grid/Grid-to-Vehice capacity | v2g_g2v_capacity | kW     | ['lad_gb_2016'] | float   |
