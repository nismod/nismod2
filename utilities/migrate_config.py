"""Migrate a configuration folder for a release of smif<1 to smif>=1

Useful to refer to the sample project within the smif directory:

https://github.com/nismod/smif/compare/develop#diff-719f473c0b17dae486b170c10c23e8c3


"""
import os
import sys
import shutil
import itertools
from excel2yaml import read_project
from ruamel.yaml import YAML

 
def _archive_old_config_folder(config_folder):
    """
    Make an archive of the project folder
    """
    shutil.make_archive(os.path.join(config_folder, '..', 'nismod2_migrate_bck'), 'zip', config_folder)

def _rename_modelrunfolder(config_folder):
    os.rename(os.path.join(config_folder, 'config/sos_model_runs'), 
              os.path.join(config_folder, 'config/model_runs'))

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
                'dtype': 'TODO',
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

def _update_narratives(project_data):
    raise NotImplementedError

def _update_project_data(config_folder):
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
    project_data = read_project(config_folder)
    # Scenarios and scenario sets -> scenarios
    project_data = _update_scenario_sets(project_data)
    # Region and Interval definitions -> dimensions
    project_data = _region_interval_to_dimensions(project_data)
    # Narrative sets and Narratives -> narratives
    project_data = _update_narratives(project_data)

    # project
    yaml = YAML()
    with open(os.path.join(config_folder, 'config', 'project.yaml'), 'w', encoding='utf-8') as project_file:
        yaml.dump(project_data, project_file)

def write(project_data):
    raise NotImplementedError

def _update_sector_model_config(config_folder):
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
    raise NotImplementedError

def _update_sos_model_config(config_folder):
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

def _move_interval_definitions(config_folder):
    """

    data/interval_definitions/* -> data/dimensions

    """
    raise NotImplementedError

def _move_region_definitions(config_folder):
    """

    data/region_definitions/* -> data/dimensions

    """
    raise NotImplementedError

def _update_scenario_data(config_folder):
    """

    data/scenarios/*.csv -> data/scenarios/*.csv

    year,region,interval,value -> <scenario['name']>,<dim>...<dim>,<provides['name']>


    """
    raise NotImplementedError

def _rewrite_configuration_data(config_folder):
    raise NotImplementedError

def main(config_folder):
    _archive_old_config_folder(config_folder)
    _rename_modelrunfolder(config_folder)
    _update_project_data(config_folder)

    _update_sector_model_config(config_folder)
    _update_sos_model_config(config_folder)

    _move_interval_definitions(config_folder)
    _move_region_definitions(config_folder)

    _update_scenario_data(config_folder)

    _rewrite_configuration_data(config_folder)

if __name__ == '__main__':

    if len(sys.argv)==2:
        main(sys.argv[1])
    else:
        print(
            'migrate_config.py path/to/smif/config'
        )