import os

template = """name: {name}
stamp: '2019-10-09'
description: "Arc Water Supply run with {description}"
sos_model: water_supply_demand
scenarios:
  socio-economic: {socioeconomic_scenario}
  water_demand_projections: {demand_scenario}
  reservoir_levels: predicted
  water_supply_data: {flows_scenario}
narratives: {{}}
timesteps:
- 2020
- 2021
- 2022
- 2023
- 2024
- 2025
- 2026
- 2027
- 2028
- 2029
- 2030
- 2031
- 2032
- 2033
- 2034
- 2035
- 2036
- 2037
- 2038
- 2039
- 2040
- 2041
- 2042
- 2043
- 2044
strategies:
  - type: pre-specified-planning
    description: {option_description}
    filename: {option_name}
    model_name: water_supply
"""

socioeconomic_scenarios = [
    'arc_baseline',
    'arc_unplanned',
    'arc_expansion',
    'arc_expansion23',
    'arc_new-cities',
    'arc_new-cities23',
]

demand_scenarios = [
    ('baseline_wrmp_2019', 'BL'),
    ('final_planning_wrmp_2019', 'FP'),
]

flows_scenarios = list(range(1, 101))

options = [
    ('arc_ws__opt_0', 'Arc Water option 0 - No Options'),
    ('arc_ws__opt_1', 'Arc Water option 1 - Severn Thames Transfer'),
    ('arc_ws__opt_2', 'Arc Water option 2 - Trent To Rutland Transfer'),
    ('arc_ws__opt_3', 'Arc Water option 3 - S Lincs Reservoir'),
    ('arc_ws__opt_4', 'Arc Water option 4 - Abingdon Storage'),
    ('arc_ws__opt_5', 'Arc Water option 5 - Beckton Reuse'),
]

for socioeconomic_scenario in socioeconomic_scenarios:
    se_short = socioeconomic_scenario.replace("arc_", "")
    try:
        os.mkdir(os.path.join("config", "model_runs", "arc_ws", se_short))
    except FileExistsError:
        pass

    for demand_scenario, demand_short in demand_scenarios:
        try:
            os.mkdir(os.path.join("config", "model_runs", "arc_ws", se_short, demand_short))
        except FileExistsError:
            pass

        for option, option_description in options:
            option_short = option.replace("arc_ws__", "")

            for flow in flows_scenarios:
                basename = "arc_ws__{}__{}__{}__{:03d}".format(
                    se_short,
                    demand_short,
                    option_short,
                    flow
                )
                fname = "{}.yml".format(basename)
                fpath = os.path.join("config", "model_runs", "arc_ws", se_short, demand_short, fname)
                name = "arc_ws/{}/{}/{}".format(
                    se_short,
                    demand_short,
                    basename
                )

                flow_name = "water_supply_data_{:03d}".format(flow)
                print(name)

                modelrun = template.format(
                    name=name,
                    description="population: {}, demand: {}, option: {}, flows: {}".format(socioeconomic_scenario, demand_scenario, option, flow_name),
                    socioeconomic_scenario=socioeconomic_scenario,
                    demand_scenario=demand_scenario,
                    option_name=option,
                    option_description=option_description,
                    flows_scenario=flow_name
                )
                with open(fpath, 'w') as fh:
                    fh.write(modelrun)
