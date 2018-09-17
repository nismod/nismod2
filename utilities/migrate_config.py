"""Migrate a configuration folder for a release of smif<1 to smif>=1

Useful to refer to the sample project within the smif directory:

https://github.com/nismod/smif/compare/develop#diff-719f473c0b17dae486b170c10c23e8c3


"""
import os
import sys
import shutil
import itertools

from logging import getLogger, basicConfig, INFO, Formatter, StreamHandler, DEBUG


from ast import literal_eval
from ruamel.yaml import YAML

LOGGER = getLogger(__name__)
LOG_FILENAME = 'migration.log'
basicConfig(filename=LOG_FILENAME,level=DEBUG, filemode='w')
# create console handler and set level to debug
ch = StreamHandler()
ch.setLevel(INFO)
# create formatter
formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
LOGGER.addHandler(ch)
 
def _archive_old_project_folder(project_folder):
    """
    Make an archive of the project folder
    """
    destination_path = os.path.join(project_folder, '..', 'nismod2_migrate_bck')

    if not os.path.exists(destination_path + '.zip'):
        shutil.make_archive(destination_path, 'zip', project_folder)

def _rename_modelrunfolder(project_folder):
    destination_folder = os.path.join(project_folder, 'config/model_runs')
    if os.path.exists(destination_folder):
        LOGGER.warning("Destination folder '%s' already exists", destination_folder)
    else:

        os.rename(os.path.join(project_folder, 'config/sos_model_runs'),
                  destination_folder)

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
    WARNING: ['provides']['dims'] and ['provides']['unit'] are best guess

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
                unit: people

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

        LOGGER.info("Updates scenario set: %s", scenario_set['name'])

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
                    ][0],
                    [
                        scenario['facets'][0]['temporal_resolution'] for scenario in old_project_data['scenarios'] 
                        if scenario['scenario_set'] == scenario_set['name']
                    ][0],
                     # best guess
                ],
                'dtype': 'float', # no info
                'unit': [
                    scenario['facets'][0]['unit'] for scenario in old_project_data['scenarios'] 
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
    - unit 
    - scenario_sets 
    - scenarios 
    - narrative_sets 
    - narratives

    To:
    
    - name
    - scenarios
    - narratives
    - dimensions
    - unit
    """
    project_config_path = os.path.join(project_folder, 'config', 'project.yml')

    project_config_data = _read_config_file(project_config_path)
    
    # Scenarios and scenario sets -> scenarios
    if 'scenario_sets' in project_config_data:
        project_config_data = _update_scenario_sets(project_config_data)
    # Region and Interval definitions -> dimensions
    if 'interval_definitions' in project_config_data and 'region_definitions' in project_config_data:
        project_config_data = _region_interval_to_dimensions(project_config_data)
    # Narrative sets and Narratives -> narratives
    if 'narrative_sets' in project_config_data:
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

        LOGGER.info("Updated sector model config file '%s'", config_file)

        config_file_path = os.path.join(config_dir, config_file)
        config_data = _read_config_file(config_file_path)

        # inputs / outputs
        for model_io in itertools.chain(config_data['inputs'], config_data['outputs']):

            dims = []
            if not model_io['temporal_resolution'] == 'national':
                dims.append(model_io['temporal_resolution'])
            
            if not model_io['temporal_resolution'] == 'annual':
                dims.append(model_io['temporal_resolution'])

            model_io['dims'] = dims

            model_io.pop('spatial_resolution')
            model_io.pop('temporal_resolution')

            model_io['dtype'] = 'float'

        # parameters
        for parameter in config_data['parameters']:
            try:
                parameter['abs_range'] = list(literal_eval(parameter.pop('absolute_range')))
            except ValueError:
                LOGGER.debug("Error reading 'absolute_range' from %s in config file '%s'", 
                    parameter['name'], config_file)
            
            try:
                parameter['exp_range'] = list(literal_eval(parameter.pop('suggested_range')))
            except ValueError:
                LOGGER.debug("Error reading 'suggested_range' from %s in config file '%s'", 
                    parameter['name'], config_file)
            try:
                parameter['default'] = parameter.pop('default_value')
            except ValueError:
                LOGGER.debug("Error reading 'default_value' from %s in config file '%s'", 
                    parameter['name'], config_file)


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
    config_dir = os.path.join(project_folder, 'config', 'sos_models')
    config_files = _get_files_in_dir(config_dir)

    project_config_dir = os.path.join(project_folder, 'config', 'project.yml')
    project_config = _read_config_file(project_config_dir)

    for config_file in config_files:

        config_file_path = os.path.join(config_dir, config_file)
        config_data = _read_config_file(config_file_path)

        # scenario_sets -> scenarios
        try:
            config_data['scenarios'] = config_data.pop('scenario_sets')
        except KeyError:
            LOGGER.debug("Cannot find key 'scenario_sets' in %s", config_file)
        # narrative_sets -> narratives
        try:
            config_data['narratives'] = config_data.pop('narrative_sets')
        except KeyError:
            LOGGER.debug("Cannot find key 'narrative_sets' in %s", config_file)


        # process dependencies
        config_data['scenario_dependencies'] = []
        config_data['model_dependencies'] = []
        for dependency in config_data['dependencies']:

            # preformat the dependency
            try:
                dependency['source'] = dependency.pop('source_model')
            except KeyError:
                LOGGER.debug("Dependency %s in %s missing 'source_model'", dependency, config_data['name'])
            try:
                dependency['source_output'] = dependency.pop('source_model_output')
            except KeyError:
                LOGGER.debug("Dependency %s in %s missing 'source_model_output'", dependency, config_data['name'])
            try:
                dependency['sink'] = dependency.pop('sink_model')
            except KeyError:
                LOGGER.debug("Dependency %s in %s missing 'sink_model'", dependency, config_data['name'])
            try:
                dependency['sink_input'] = dependency.pop('sink_model_input')
            except KeyError:
                LOGGER.debug("Dependency %s in %s missing 'sink_model_input'", dependency, config_data['name'])
            
            # split up list
            if dependency['source'] in [scenario['name'] for scenario in project_config['scenarios']]:
                config_data['scenario_dependencies'].append(dependency)
            else:
                config_data['model_dependencies'].append(dependency)
        config_data.pop('dependencies')

        # drop keys
        config_data.pop('max_iterations')
        config_data.pop('convergence_absolute_tolerance')

        _write_config_file(config_file_path, config_data)
        LOGGER.info("Sucessfully updated sos_model config: %s", config_file_path)

def _move_region_interval_definitions(project_folder):
    """

    data/interval_definitions/* -> data/dimensions
    data/region_definitions/* -> data/dimensions

    """
    region_def_dir = os.path.join(project_folder, 'data', 'region_definitions')
    interval_def_dir = os.path.join(project_folder, 'data', 'interval_definitions')
    dimension_dir = os.path.join(project_folder, 'data', 'dimensions')

    try:
        os.mkdir(dimension_dir)
    except:
        pass

    for def_dir in [region_def_dir, interval_def_dir]:

        def_dir_files = os.listdir(def_dir)
        for def_dir_file in def_dir_files:
            try:
                shutil.rmtree(os.path.join(dimension_dir, def_dir_file))
            except:
                pass
            shutil.move(os.path.join(def_dir, def_dir_file), os.path.join(dimension_dir, def_dir_file))

    os.rmdir(region_def_dir)
    os.rmdir(interval_def_dir)

def main(project_folder):
    # _archive_old_project_folder(project_folder)
    _rename_modelrunfolder(project_folder)
    _update_project_data(project_folder)

    _update_sector_model_config(project_folder)

    _update_sos_model_config(project_folder)

    _move_region_interval_definitions(project_folder)

if __name__ == '__main__':

    if len(sys.argv)==2:
        main(sys.argv[1])
    else:
        print(
            'migrate_config.py path/to/smif/config'
        )