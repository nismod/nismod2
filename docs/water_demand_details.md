# Water Demand

[&lt; Back to Water](./water-supply.html)

Water demand modified by population scenarios.

# Inputs

| description                     | name                    | unit          | dims                     | dtype   |
|:--------------------------------|:------------------------|:--------------|:-------------------------|:--------|
| Population                      | population              | people        | ['water_resource_zones'] | float   |
| Constant water demand component | constant_water_demand   | Ml/day        | ['water_resource_zones'] | float   |
| Per-capita water demand         | per_capita_water_demand | Ml/person/day | ['water_resource_zones'] | float   |

# Parameters

No parameters.

# Outputs

| description         | name         | unit   | dims                     | dtype   |
|:--------------------|:-------------|:-------|:-------------------------|:--------|
| Public water demand | water_demand | Ml/day | ['water_resource_zones'] | float   |
