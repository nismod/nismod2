"""Migrate a configuration folder for a release of smif<1 to smif>=1

Useful to refer to the sample project within the smif directory:

https://github.com/nismod/smif/compare/develop#diff-719f473c0b17dae486b170c10c23e8c3


"""
import os
import sys
import shutil
import itertools

from ast import literal_eval
from ruamel.yaml import YAML

 
def _archive_old_project_folder(project_folder):
    """
    Make an archive of the project folder
    """
    shutil.make_archive(os.path.join(project_folder, '..', 'nismod2_migrate_bck'), 'zip', project_folder)

def _rename_modelrunfolder(project_folder):
    os.rename(os.path.join(project_folder, 'config/sos_model_runs'), 
              os.path.join(project_folder, 'config/model_runs'))

def _read_config_file(filepath):
    yaml = YAML()
    with open(filepath, encoding='utf-8') as file:
        data = yaml.load(file)

    for key, value in data.items():
        if value == None:
            data[key] = []

    return data

def _write_config_file(filepath, data):
    yaml = YAML()
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)

def _get_files_in_dir(dirpath):
    return [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]

def _update_scenario_sets(old_project_data):
    """
    WARNING: ['provides']['dims'] and ['provides']['units'] are best guess

    From

        scenario_sets:
          - name: population
            description: Growth in UK population
            facets:
            - name: population
                description: ''

        scenarios:
          - name: population_low
            description: Low population for the UK
            scenario_set: population
            facets:
            - name: population
                filename: uk_population_by_district_codes_Low.csv
                spatial_resolution: lad_uk_2016
                temporal_resolution: annual
                units: people

    To

        scenarios:
          - name: population
            description: Growth in UK population
            provides:
            - name: population
              description: ''
              dims:
              - lad_uk_2016
              dtype: int
              unit: people
            variants:
            - name: population_low
              description: Central Population (Low)
              data:
                population: population_low.csv

    """
    new_scenarios = []

    for scenario_set in old_project_data['scenario_sets']:

        # General
        new_scenario = {
            'name': scenario_set['name'],
            'description': scenario_set['description'],
            'provides': [],
            'variants': []
        }

        # provides
        for facet in scenario_set['facets']:
            new_scenario['provides'].append({
                'name': facet['name'],
                'description': facet['description'],
                'dims': [
                    [
                        scenario['facets'][0]['spatial_resolution'] for scenario in old_project_data['scenarios'] 
                        if scenario['scenario_set'] == scenario_set['name']
                    ][0] # best guess
                ],
                'dtype': 'TODO', # no info
                'unit': [
                    scenario['facets'][0]['units'] for scenario in old_project_data['scenarios'] 
                    if scenario['scenario_set'] == scenario_set['name']
                ][0] # best guess
            })

        # variants
        for scenario in old_project_data['scenarios']:
            if scenario['scenario_set'] == new_scenario['name']:
                new_scenario['variants'].append({
                    'name': scenario['name'],
                    'description': scenario['description'],
                    'data': {
                        facet['name']: facet['filename'] for facet in scenario['facets']
                    }
                })

        new_scenarios.append(new_scenario)

    old_project_data['scenarios'] = new_scenarios
    old_project_data.pop('scenario_sets')

    return old_project_data

def _region_interval_to_dimensions(old_project_data):
    """
    From

    interval_definitions:
      - name: annual
        description: ''
        filename: annual_intervals.csv
    region_definitions:
      - name: national
        description: ''
        filename: uk_nations_shp/regions.shp
      - name: oxfordshire
        description: ''
        filename: oxfordshire/regions.geojson

    To

    dimensions:
      - name: annual
        description: ''
        elements: annual_intervals.csv
      - name: national
        description: ''
        elements: uk_nations_shp/regions.shp
      - name: oxfordshire
        description: ''
        elements: oxfordshire/regions.geojson
    """
    dimensions = []
    definitions = itertools.chain(
        old_project_data['interval_definitions'], 
        old_project_data['region_definitions']
    )
    for definition in definitions:
        dimensions.append({
            'name': definition['name'],
            'description': definition['description'],
            'elements': definition['filename']
        })
    
    old_project_data.pop('interval_definitions')
    old_project_data.pop('region_definitions')
    old_project_data['dimensions'] = dimensions

    return old_project_data

def _update_narratives(old_project_data):
    """
    WARNING: ['variant'] are best guess

    From:

    narrative_sets:
    - name: technology
      description: Describes the evolution of technology
    narratives:
    - name: High Tech Demand Side Management
      description: High penetration of SMART technology on the demand side
      filename: high_tech_dsm.yml
      narrative_set: technology

    To:

    narratives:
    - name: technology
        description: Describes the evolution of technology
        provides:
        - name: smart_meter_savings
          description: The savings from smart meters
          dtype: float
          unit: '%'
        - name: clever_water_meter_savings
          description: The savings from smart water meters
          dtype: float
          unit: '%'
        - name: per_capita_water_demand
          description: The assumed per capita demand for water
          dtype: float
          unit: liter/person
        variants:
        - name: high_tech_dsm
          description: High penetration of SMART technology on the demand side
          data:
            smart_meter_savings: high_tech_dsm.csv
            clever_water_meter_savings: high_tech_dsm.csv
            per_capita_water_demand: high_tech_dsm.csv  
    """

    new_narratives = []

    for narrative_set in old_project_data['narrative_sets']:

        # General
        new_narrative = {
            'name': narrative_set['name'],
            'description': narrative_set['description'],
            'provides': [],
            'variants': []
        }

        # provides
        for narrative in old_project_data['narratives']:
            if narrative['narrative_set'] == new_narrative['name']:
                new_narrative['provides'].append({
                    'name': narrative['name'],
                    'description': narrative['description'],
                    'dtype': 'TODO', # no info
                    'unit': 'TODO' # no info
                })

        # variants
        new_narrative['variants'].append({
            'name': 'TODO', # no info
            'description': 'TODO', # no info
            'data': {provide['name']: old_project_data['narratives'][0]['filename'] for provide in new_narrative['provides']}
        }) # best guess

        new_narratives.append(new_narrative)

    old_project_data['narratives'] = new_narratives
    old_project_data.pop('narrative_sets')

    return old_project_data

def _update_project_data(project_folder):
    """
    From:

    - name
    - region_definitions 
    - interval_definitions 
    - units 
    - scenario_sets 
    - scenarios 
    - narrative_sets 
    - narratives

    To:
    
    - name
    - scenarios
    - narratives
    - dimensions
    - units
    """
    project_config_path = os.path.join(project_folder, 'config', 'project.yml')

    project_config_data = _read_config_file(project_config_path)
    # Scenarios and scenario sets -> scenarios
    project_config_data = _update_scenario_sets(project_config_data)
    # Region and Interval definitions -> dimensions
    project_config_data = _region_interval_to_dimensions(project_config_data)
    # Narrative sets and Narratives -> narratives
    project_config_data = _update_narratives(project_config_data)

    # project
    _write_config_file(project_config_path, project_config_data)

def write(project_data):
    raise NotImplementedError

def _update_sector_model_config(project_folder):
    """Inputs, outputs and parameters all use Spec definition

    inputs

    - spatial_resolution and temporal_resolution -> dims
    - add ``dtype``
    - units -> unit
    - remove ``annual`` (now implicit)

    outputs

    - spatial_resolution and temporal_resolution -> dims
    - add ``dtype``
    - units -> unit
    - remove ``annual`` (now implicit)

    parameters

    - absolute_range -> abs_range
      - tuple -> list
    - suggested_range -> exp_range
      - tuple -> list
    - default_value -> default
    - add `dtype`
    - units -> unit

    """
    config_dir = os.path.join(project_folder, 'config', 'sector_models')
    config_files = _get_files_in_dir(config_dir)

    for config_file in config_files:

        config_file_path = os.path.join(config_dir, config_file)
        config_data = _read_config_file(config_file_path)

        # inputs / outputs
        for model_io in itertools.chain(config_data['inputs'], config_data['outputs']):
            model_io['dims'] = [
                model_io['spatial_resolution'],
                # model_io['temporal_resolution'], // remove annual (now implicit)
            ]
            model_io.pop('spatial_resolution')
            model_io.pop('temporal_resolution')

            model_io['dtype'] = 'TODO'

        # parameters
        for parameter in config_data['parameters']:
            parameter['abs_range'] = list(literal_eval(parameter['absolute_range']))
            parameter.pop('absolute_range')
            parameter['exp_range'] = list(literal_eval(parameter['suggested_range']))
            parameter.pop('suggested_range')
            parameter['default'] = parameter['default_value']
            parameter.pop('default_value')
            parameter['dtype'] = 'TODO'


        _write_config_file(config_file_path, config_data)

def _update_sos_model_config(project_folder):
    """

    scenario_sets -> scenarios
    narrative_sets -> narratives

    dependencies -> model_dependencies
    OR
    dependencies -> scenario_dependencies

    source_model -> source 
    source_model_output -> source_output
    sink_model -> sink
    sink_model_input -> sink_input

    Remove keys

        max_iterations
        convergence_absolute_tolerance

    """
    raise NotImplementedError

def _move_interval_definitions(project_folder):
    """

    data/interval_definitions/* -> data/dimensions

    """
    raise NotImplementedError

def _move_region_definitions(project_folder):
    """

    data/region_definitions/* -> data/dimensions

    """
    raise NotImplementedError

def _update_scenario_data(project_folder):
    """

    data/scenarios/*.csv -> data/scenarios/*.csv

    year,region,interval,value -> <scenario['name']>,<dim>...<dim>,<provides['name']>


    """
    raise NotImplementedError

def _rewrite_configuration_data(project_folder):
    raise NotImplementedError

def main(project_folder):
    _archive_old_project_folder(project_folder)
    _rename_modelrunfolder(project_folder)
    _update_project_data(project_folder)

    _update_sector_model_config(project_folder)
    _update_sos_model_config(project_folder)

    _move_interval_definitions(project_folder)
    _move_region_definitions(project_folder)

    _update_scenario_data(project_folder)

    _rewrite_configuration_data(project_folder)

if __name__ == '__main__':

    if len(sys.argv)==2:
        main(sys.argv[1])
    else:
        print(
            'migrate_config.py path/to/smif/config'
        )